export const studentTheme = {
  name: 'orange',
  colors: {
    primary: '#C96030',
    secondary: '#F18B5B',
    background: '#FFE6CE',
    surface: '#FFF5E7',
    text: {
      primary: '#C96030',
      secondary: '#F18B5B',
      inverse: '#FFFFFF'
    },
    border: '#C96030',
    hover: {
      primary: '#E86A3F',
      background: 'rgba(255, 245, 231, 0.5)'
    },
    shadow: 'rgba(241, 139, 91, 0.1)'
  }
}

export const teacherTheme = {
  name: 'blue',
  colors: {
    primary: '#008AC5',
    secondary: '#276884',
    tertiary: '#1d5369',
    background: '#CDF4FF',
    surface: '#F2FCFF',
    text: {
      primary: '#276884',
      secondary: '#008AC5',
      tertiary: '#1d5369',
      inverse: '#CDF4FF'
    },
    border: '#008AC5',
    hover: {
      primary: '#006B9A',
      background: 'rgba(205, 244, 255, 0.5)'
    },
    shadow: 'rgba(0, 138, 197, 0.1)'
  }
}

export const themes = {
  orange: studentTheme,
  blue: teacherTheme
}

export function getTheme(themeName) {
  return themes[themeName] || teacherTheme
}
