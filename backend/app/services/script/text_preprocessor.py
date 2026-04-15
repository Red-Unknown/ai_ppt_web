import re

class MathTTSConverter:
    def __init__(self):
        self.basic_conversions = [
            ('π', '派'),
            ('√', '根号'),
            ('∞', '无穷大'),
            ('∫', '积分'),
            ('∑', '求和'),
            ('∂', '偏导数'),
            ('∇', 'nabla算子'),
            ('·', '点乘'),
            ('×', '叉乘'),
            ('·', '点'),
            ('θ', 'theta角'),
            ('α', '阿尔法'),
            ('β', '贝塔'),
            ('γ', '伽马'),
            ('δ', '德尔塔'),
            ('ε', 'epsilon'),
            ('λ', '拉姆达'),
            ('μ', '缪'),
            ('σ', '西格玛'),
            ('φ', 'phi'),
            ('ψ', 'psi'),
            ('ω', 'omega'),
            ('→', '趋向于'),
            ('←', '来自于'),
            ('↔', '等价于'),
            ('⇒', '可以推出'),
            ('⇔', '当且仅当'),
            ('∈', '属于'),
            ('∉', '不属于'),
            ('⊂', '包含于'),
            ('⊃', '包含'),
            ('∩', '交集'),
            ('∪', '并集'),
            ('∀', '对于所有'),
            ('∃', '存在'),
            ('∄', '不存在'),
            ('∴', '因此'),
            ('∵', '因为'),
            ('±', '正负'),
            ('∓', '负正'),
            ('×', '乘以'),
            ('÷', '除以'),
            ('≠', '不等于'),
            ('≤', '小于等于'),
            ('≥', '大于等于'),
            ('≡', '恒等于'),
            ('≈', '约等于'),
            ('∝', '成正比'),
        ]
        
        self.function_conversions = [
            ('sin', '正弦'),
            ('cos', '余弦'),
            ('tan', '正切'),
            ('cot', '余切'),
            ('sec', '正割'),
            ('csc', '余割'),
            ('sinh', '双曲正弦'),
            ('cosh', '双曲余弦'),
            ('tanh', '双曲正切'),
            ('arcsin', '反正弦'),
            ('arccos', '反余弦'),
            ('arctan', '反正切'),
            ('log', '对数'),
            ('ln', '自然对数'),
            ('exp', '指数'),
            ('sqrt', '根号'),
            ('abs', '绝对值'),
            ('det', '行列式'),
            ('rank', '秩'),
            ('tr', '迹'),
            ('lim', '极限'),
            ('max', '最大值'),
            ('min', '最小值'),
            ('sup', '上确界'),
            ('inf', '下确界'),
            ('gcd', '最大公约数'),
            ('lcm', '最小公倍数'),
        ]
        
        self.special_constants = [
            ('e', '自然常数e'),
            ('pi', '派'),
            ('i', '虚数单位i'),
            ('j', '虚数单位j'),
            ('phi', '黄金比例'),
        ]
        
        self.famous_formulas = [
            ('E=mc^2', '能量E等于质量m乘以光速c的平方'),
            ('E = mc^2', '能量E等于质量m乘以光速c的平方'),
            ('F=ma', '力F等于质量m乘以加速度a'),
            ('F = ma', '力F等于质量m乘以加速度a'),
            ('PV=nRT', 'P乘以V等于n乘以R乘以T'),
            ('PV = nRT', 'P乘以V等于n乘以R乘以T'),
            ('a^2 + b^2 = c^2', 'a的平方加b的平方等于c的平方'),
            ('a^2+b^2=c^2', 'a的平方加b的平方等于c的平方'),
            ('e^(iπ) + 1 = 0', 'e的i派次方加一等于零'),
            ('e^(iπ)+1=0', 'e的i派次方加一等于零'),
        ]

    def convert(self, text):
        text = self._normalize_text(text)
        text = self._convert_famous_formulas(text)
        text = self._convert_special_constants(text)
        text = self._convert_functions(text)
        text = self._convert_basic_symbols(text)
        text = self._convert_subscripts(text)
        text = self._convert_exponents(text)
        text = self._convert_fractions(text)
        text = self._convert_parentheses(text)
        text = self._convert_operators(text)
        text = self._clean_text(text)
        return text

    def _normalize_text(self, text):
        text = text.replace('²', '^2').replace('³', '^3').replace('⁴', '^4')
        text = text.replace('₀', '_0').replace('₁', '_1').replace('₂', '_2').replace('₃', '_3')
        text = text.replace('₄', '_4').replace('₅', '_5').replace('₆', '_6').replace('₇', '_7')
        text = text.replace('₈', '_8').replace('₉', '_9').replace('ₙ', '_n')
        return text

    def _convert_famous_formulas(self, text):
        for formula, description in self.famous_formulas:
            text = text.replace(formula, description)
        return text

    def _convert_special_constants(self, text):
        for symbol, name in self.special_constants:
            text = re.sub(r'(?<![a-zA-Z])' + re.escape(symbol) + r'(?![a-zA-Z])', name, text)
        return text

    def _convert_functions(self, text):
        for func_name, chinese_name in self.function_conversions:
            pattern = r'(?<![a-zA-Z])' + re.escape(func_name) + r'\('
            text = re.sub(pattern, chinese_name + '(', text)
        return text

    def _convert_basic_symbols(self, text):
        for symbol, name in self.basic_conversions:
            text = text.replace(symbol, name)
        return text

    def _convert_subscripts(self, text):
        text = re.sub(r'_(\d+)', r'下标\1', text)
        text = re.sub(r'_([a-zA-Z])', r'下标\1', text)
        text = re.sub(r'下标0', '下标零', text)
        text = re.sub(r'下标1', '下标一', text)
        text = re.sub(r'下标2', '下标二', text)
        text = re.sub(r'下标3', '下标三', text)
        text = re.sub(r'下标4', '下标四', text)
        text = re.sub(r'下标5', '下标五', text)
        return text

    def _convert_exponents(self, text):
        text = re.sub(r'\^(\d+)', r'的\1次方', text)
        text = re.sub(r'\^([a-zA-Z])', r'的\1次方', text)
        text = re.sub(r'的2次方', '的平方', text)
        text = re.sub(r'的3次方', '的立方', text)
        text = re.sub(r'的1次方', '', text)
        return text

    def _convert_fractions(self, text):
        text = re.sub(r'(\d+)/(\d+)', r'\1分之\2', text)
        text = re.sub(r'(\d+)/(\d+)', r'\1分之\2', text)
        return text

    def _convert_parentheses(self, text):
        text = text.replace('(', '，').replace(')', '，')
        text = text.replace('[', '，').replace(']', '，')
        text = text.replace('{', '，').replace('}', '，')
        return text

    def _convert_operators(self, text):
        text = text.replace('=', '等于')
        text = text.replace('+', '加')
        text = text.replace('-', '减')
        text = text.replace('*', '乘以')
        text = text.replace('/', '除以')
        return text

    def _clean_text(self, text):
        text = ' '.join(text.split())
        text = re.sub(r'，+', '，', text)
        text = re.sub(r'([，。！？])\1+', r'\1', text)
        text = re.sub(r'等于等于', '等于', text)
        text = re.sub(r'加加', '加', text)
        text = re.sub(r'减减', '减', text)
        text = re.sub(r'乘以乘以', '乘以', text)
        text = re.sub(r'除以除以', '除以', text)
        
        if text.endswith('，'):
            text = text[:-1]
        
        text = text.strip()
        return text

def preprocess_text_for_tts(text: str) -> str:
    converter = MathTTSConverter()
    return converter.convert(text)