import logging
import threading
import time
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field
from enum import Enum
from queue import Queue, Empty, Full

from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel

from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class PoolStatus(Enum):
    IDLE = "idle"
    ACTIVE = "active"
    UNHEALTHY = "unhealthy"
    CLOSED = "closed"


class PoolError(Exception):
    pass


class PoolTimeoutError(PoolError):
    pass


class PoolExhaustedError(PoolError):
    pass


class LLMConfigurationError(PoolError):
    pass


@dataclass
class LLMPoolConfig:
    max_connections: int = 20
    min_idle_connections: int = 5
    connection_timeout: float = 30.0
    idle_timeout: float = 300.0
    health_check_interval: float = 60.0
    max_retries: int = 3


@dataclass
class LLMClientWrapper:
    client: BaseChatModel
    scenario: str
    status: PoolStatus = PoolStatus.IDLE
    created_at: float = field(default_factory=time.time)
    last_used_at: float = field(default_factory=time.time)
    use_count: int = 0


class LLMPool:
    def __init__(self, config: Optional[LLMPoolConfig] = None):
        self.config = config or LLMPoolConfig()
        self._lock = threading.RLock()
        self._condition = threading.Condition(self._lock)
        
        self._pools: Dict[str, Queue] = {}
        self._active_clients: Dict[str, List[LLMClientWrapper]] = {}
        self._scenarios: Dict[str, Dict[str, Any]] = {}
        
        self._initialized = False
        self._shutdown = False
        self._health_check_thread: Optional[threading.Thread] = None
        self._stop_health_check = threading.Event()

        self._scenario_configs = {
            "qa": {
                "model": settings.DEEPSEEK_MODEL,
                "temperature": 0.7,
                "max_tokens": 4000,
                "api_key": settings.DEEPSEEK_API_KEY,
                "base_url": settings.DEEPSEEK_BASE_URL,
            },
            "reasoner": {
                "model": settings.DEEPSEEK_REASONER_MODEL,
                "temperature": 0.6,
                "max_tokens": 4000,
                "api_key": settings.DEEPSEEK_API_KEY,
                "base_url": settings.DEEPSEEK_BASE_URL,
            },
            "summary": {
                "model": settings.DEEPSEEK_MODEL,
                "temperature": 0.3,
                "max_tokens": 4000,
                "api_key": settings.DEEPSEEK_API_KEY,
                "base_url": settings.DEEPSEEK_BASE_URL,
            },
            "translation": {
                "model": settings.DEEPSEEK_MODEL,
                "temperature": 0.1,
                "max_tokens": 4000,
                "api_key": settings.DEEPSEEK_API_KEY,
                "base_url": settings.DEEPSEEK_BASE_URL,
            },
        }
        
        if settings.KIMI_API_KEY:
            for scenario in ["qa", "reasoner", "summary", "translation"]:
                self._scenario_configs[f"{scenario}_kimi"] = {
                    "model": settings.KIMI_MODEL,
                    "temperature": self._scenario_configs[scenario]["temperature"],
                    "max_tokens": settings.KIMI_MAX_TOKENS,
                    "api_key": settings.KIMI_API_KEY,
                    "base_url": settings.KIMI_BASE_URL,
                }
        
        if settings.OPENAI_API_KEY:
            for scenario in ["qa", "reasoner", "summary", "translation"]:
                self._scenario_configs[f"{scenario}_gpt"] = {
                    "model": "gpt-4o",
                    "temperature": self._scenario_configs[scenario]["temperature"],
                    "max_tokens": 2048,
                    "api_key": settings.OPENAI_API_KEY,
                    "base_url": None,
                }

        if settings.EFFECTIVE_QWEN_API_KEY:
            self._scenario_configs["qwen"] = {
                "model": settings.QWEN_MODEL,
                "temperature": settings.QWEN_TEMPERATURE,
                "max_tokens": settings.QWEN_MAX_TOKENS,
                "api_key": settings.EFFECTIVE_QWEN_API_KEY,
                "base_url": settings.EFFECTIVE_QWEN_BASE_URL,
            }
            self._scenario_configs["qwen_vision"] = {
                "model": settings.QWEN_VISION_MODEL,
                "temperature": settings.QWEN_TEMPERATURE,
                "max_tokens": settings.QWEN_MAX_TOKENS,
                "api_key": settings.EFFECTIVE_QWEN_API_KEY,
                "base_url": settings.EFFECTIVE_QWEN_BASE_URL,
                "vision": True,
            }
            for scenario in ["qa", "reasoner", "summary", "translation"]:
                self._scenario_configs[f"{scenario}_qwen"] = {
                    "model": settings.QWEN_MODEL,
                    "temperature": self._scenario_configs[scenario]["temperature"],
                    "max_tokens": settings.QWEN_MAX_TOKENS,
                    "api_key": settings.EFFECTIVE_QWEN_API_KEY,
                    "base_url": settings.EFFECTIVE_QWEN_BASE_URL,
                }
                self._scenario_configs[f"{scenario}_qwen_vision"] = {
                    "model": settings.QWEN_VISION_MODEL,
                    "temperature": self._scenario_configs[scenario]["temperature"],
                    "max_tokens": settings.QWEN_MAX_TOKENS,
                    "api_key": settings.EFFECTIVE_QWEN_API_KEY,
                    "base_url": settings.EFFECTIVE_QWEN_BASE_URL,
                    "vision": True,
                }

        logger.info(f"LLMPool initialized with config: max_connections={self.config.max_connections}, "
                   f"min_idle={self.config.min_idle_connections}, timeout={self.config.connection_timeout}")

    def _create_client(self, scenario: str) -> BaseChatModel:
        if scenario not in self._scenario_configs:
            raise ValueError(f"Unknown scenario: {scenario}")
        
        config = self._scenario_configs[scenario]
        
        api_key = config.get("api_key")
        if not api_key:
            raise LLMConfigurationError(
                f"API key not configured for scenario: {scenario}. "
                f"Please set the appropriate environment variable (e.g., QWEN_API_KEY)."
            )
        
        is_vision = config.get("vision", False)
        
        if is_vision and "qwen" in scenario.lower() and "vl" in config.get("model", "").lower():
            client = ChatOpenAI(
                model=config["model"],
                api_key=api_key,
                base_url=config["base_url"],
                temperature=config["temperature"],
                max_tokens=config["max_tokens"],
                streaming=True,
                max_retries=self.config.max_retries,
            )
        else:
            client = ChatOpenAI(
                model=config["model"],
                api_key=api_key,
                base_url=config["base_url"],
                temperature=config["temperature"],
                max_tokens=config["max_tokens"],
                streaming=True,
                max_retries=self.config.max_retries,
            )
        
        logger.debug(f"Created new LLM client for scenario: {scenario}")
        return client

    def initialize(self) -> None:
        with self._lock:
            if self._initialized:
                logger.warning("LLMPool already initialized")
                return
            
            logger.info("Initializing LLM connection pool...")
            
            for scenario in self._scenario_configs:
                self._pools[scenario] = Queue(maxsize=self.config.max_connections)
                self._active_clients[scenario] = []
                
                for _ in range(self.config.min_idle_connections):
                    try:
                        client = self._create_client(scenario)
                        wrapper = LLMClientWrapper(
                            client=client,
                            scenario=scenario,
                            status=PoolStatus.IDLE
                        )
                        self._pools[scenario].put(wrapper, block=False)
                    except Exception as e:
                        logger.error(f"Failed to create initial client for {scenario}: {e}")
            
            self._initialized = True
            self._start_health_check()
            logger.info(f"LLMPool initialized successfully with {len(self._scenario_configs)} scenarios")

    def _start_health_check(self) -> None:
        if self._health_check_thread is not None:
            return
        
        self._stop_health_check.clear()
        self._health_check_thread = threading.Thread(
            target=self._health_check_loop,
            daemon=True,
            name="llm-pool-health-check"
        )
        self._health_check_thread.start()
        logger.info("Health check thread started")

    def _health_check_loop(self) -> None:
        while not self._stop_health_check.is_set():
            time.sleep(self.config.health_check_interval)
            if self._shutdown:
                break
            try:
                self.health_check()
            except Exception as e:
                logger.error(f"Health check error: {e}")

    def health_check(self) -> Dict[str, int]:
        checked = {}
        with self._lock:
            for scenario, pool in self._pools.items():
                healthy_count = 0
                unhealthy_count = 0
                
                temp_clients = []
                while not pool.empty():
                    try:
                        wrapper = pool.get_nowait()
                        if self._is_client_healthy(wrapper):
                            healthy_count += 1
                            temp_clients.append(wrapper)
                        else:
                            unhealthy_count += 1
                            logger.warning(f"Removed unhealthy client for scenario: {scenario}")
                    except Empty:
                        break
                
                for wrapper in temp_clients:
                    pool.put(wrapper, block=False)
                
                for wrapper in self._active_clients[scenario]:
                    if self._is_client_healthy(wrapper):
                        healthy_count += 1
                    else:
                        unhealthy_count += 1
                
                checked[scenario] = {"healthy": healthy_count, "unhealthy": unhealthy_count}
        
        logger.debug(f"Health check result: {checked}")
        return checked

    def _is_client_healthy(self, wrapper: LLMClientWrapper) -> bool:
        current_time = time.time()
        if current_time - wrapper.created_at > self.config.idle_timeout * 2:
            return False
        return True

    def get_client(self, scenario: str = "qa", timeout: Optional[float] = None) -> BaseChatModel:
        if not self._initialized:
            raise PoolError("Pool not initialized. Call initialize() first.")
        
        if self._shutdown:
            raise PoolError("Pool is shut down.")
        
        if scenario not in self._pools:
            raise ValueError(f"Unknown scenario: {scenario}")
        
        timeout = timeout or self.config.connection_timeout
        deadline = time.time() + timeout
        
        with self._condition:
            while True:
                pool = self._pools[scenario]
                total_active = len(self._active_clients[scenario])
                
                if not pool.empty():
                    try:
                        wrapper = pool.get_nowait()
                        wrapper.status = PoolStatus.ACTIVE
                        wrapper.last_used_at = time.time()
                        wrapper.use_count += 1
                        self._active_clients[scenario].append(wrapper)
                        
                        logger.debug(f"Retrieved client for {scenario}, active: {total_active + 1}")
                        return wrapper.client
                    except Empty:
                        pass
                
                if total_active >= self.config.max_connections:
                    remaining_time = deadline - time.time()
                    if remaining_time <= 0:
                        raise PoolTimeoutError(
                            f"Timeout waiting for available connection in {scenario}. "
                            f"Active: {total_active}, Max: {self.config.max_connections}"
                        )
                    
                    logger.debug(f"Waiting for available connection in {scenario}, active: {total_active}")
                    self._condition.wait(timeout=min(remaining_time, 1.0))
                else:
                    try:
                        client = self._create_client(scenario)
                        wrapper = LLMClientWrapper(
                            client=client,
                            scenario=scenario,
                            status=PoolStatus.ACTIVE
                        )
                        wrapper.use_count = 1
                        self._active_clients[scenario].append(wrapper)
                        
                        logger.debug(f"Created new client for {scenario}, active: {total_active + 1}")
                        return wrapper.client
                    except Exception as e:
                        logger.error(f"Failed to create new client for {scenario}: {e}")
                        raise PoolError(f"Failed to create client: {e}")

    def release_client(self, client: BaseChatModel) -> None:
        with self._lock:
            for scenario, active_list in self._active_clients.items():
                for i, wrapper in enumerate(active_list):
                    if wrapper.client is client:
                        active_list.pop(i)
                        
                        if self._shutdown:
                            logger.debug(f"Pool shutting down, not returning client to pool")
                            return
                        
                        pool = self._pools[scenario]
                        if pool.qsize() < self.config.max_connections:
                            wrapper.status = PoolStatus.IDLE
                            wrapper.last_used_at = time.time()
                            
                            try:
                                pool.put(wrapper, block=False)
                                logger.debug(f"Released client for {scenario}, active: {len(active_list)}")
                            except Full:
                                logger.warning(f"Pool full for {scenario}, discarding client")
                        else:
                            logger.debug(f"Pool full for {scenario}, discarding client")
                        
                        self._condition.notify()
                        return
            
            logger.warning("Attempted to release unknown client")

    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            status = {
                "initialized": self._initialized,
                "shutdown": self._shutdown,
                "config": {
                    "max_connections": self.config.max_connections,
                    "min_idle_connections": self.config.min_idle_connections,
                    "connection_timeout": self.config.connection_timeout,
                    "idle_timeout": self.config.idle_timeout,
                    "health_check_interval": self.config.health_check_interval,
                },
                "scenarios": {}
            }
            
            for scenario in self._pools:
                pool = self._pools[scenario]
                active = len(self._active_clients[scenario])
                idle = pool.qsize()
                
                status["scenarios"][scenario] = {
                    "active_connections": active,
                    "idle_connections": idle,
                    "total_connections": active + idle,
                }
            
            return status

    def shutdown(self) -> None:
        logger.info("Shutting down LLM connection pool...")
        
        self._stop_health_check.set()
        if self._health_check_thread:
            self._health_check_thread.join(timeout=5.0)
        
        with self._lock:
            self._shutdown = True
            
            for scenario, pool in self._pools.items():
                while not pool.empty():
                    try:
                        pool.get_nowait()
                    except Empty:
                        break
            
            for scenario, active_list in self._active_clients.items():
                active_list.clear()
            
            self._initialized = False
            logger.info("LLMPool shut down successfully")

    def register_scenario(self, scenario: str, config: Dict[str, Any]) -> None:
        with self._lock:
            if scenario in self._pools:
                logger.warning(f"Scenario {scenario} already registered, overwriting")
            
            self._scenario_configs[scenario] = config
            self._pools[scenario] = Queue(maxsize=self.config.max_connections)
            self._active_clients[scenario] = []
            
            if self._initialized:
                for _ in range(self.config.min_idle_connections):
                    try:
                        client = self._create_client(scenario)
                        wrapper = LLMClientWrapper(
                            client=client,
                            scenario=scenario,
                            status=PoolStatus.IDLE
                        )
                        self._pools[scenario].put(wrapper, block=False)
                    except Exception as e:
                        logger.error(f"Failed to create initial client for {scenario}: {e}")
            
            logger.info(f"Registered new scenario: {scenario}")


_global_pool: Optional[LLMPool] = None
_pool_lock = threading.Lock()


def get_global_pool() -> LLMPool:
    global _global_pool
    if _global_pool is None:
        with _pool_lock:
            if _global_pool is None:
                _global_pool = LLMPool()
    return _global_pool


def initialize_pool(config: Optional[LLMPoolConfig] = None) -> None:
    pool = get_global_pool()
    if config:
        pool.__init__(config)
    pool.initialize()


def get_llm_client(scenario: str = "qa", timeout: Optional[float] = None, model: Optional[str] = None) -> BaseChatModel:
    pool = get_global_pool()
    if model is not None:
        scenario = _resolve_model_to_scenario(model, scenario)
    return pool.get_client(scenario=scenario, timeout=timeout)


def _resolve_model_to_scenario(model: str, default_scenario: str = "qa") -> str:
    model_lower = model.lower().strip()
    
    if model_lower in ("qwen", "qwen-turbo", "qwen-plus"):
        return "qwen"
    elif model_lower in ("qwen-vl", "qwen-vl-plus", "qwen-vl-max", "qwen_vision"):
        return "qwen_vision"
    elif model_lower in ("deepseek", "deepseek-chat"):
        return default_scenario
    elif model_lower in ("gpt", "gpt-4", "gpt-4o"):
        return f"{default_scenario}_gpt"
    elif model_lower in ("kimi", "moonshot"):
        return f"{default_scenario}_kimi"
    else:
        supported_models = ["qwen", "qwen-vl", "deepseek", "gpt", "kimi"]
        raise ValueError(f"Unsupported model: {model}. Supported models: {supported_models}")


def release_llm_client(client: BaseChatModel) -> None:
    pool = get_global_pool()
    pool.release_client(client)


def get_pool_status() -> Dict[str, Any]:
    pool = get_global_pool()
    return pool.get_status()


def shutdown_pool() -> None:
    pool = get_global_pool()
    pool.shutdown()


class LLMPoolContext:
    def __init__(self, scenario: str = "qa", timeout: Optional[float] = None, model: Optional[str] = None):
        self.scenario = scenario
        self.timeout = timeout
        self.model = model
        self.client: Optional[BaseChatModel] = None
    
    def __enter__(self) -> BaseChatModel:
        self.client = get_llm_client(self.scenario, self.timeout, self.model)
        return self.client
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.client is not None:
            release_llm_client(self.client)
