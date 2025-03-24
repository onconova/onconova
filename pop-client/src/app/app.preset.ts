import { definePreset } from '@primeng/themes';
import Aura from '@primeng/themes/aura';

const shades: number[] = [50,100, 200, 300, 400, 500, 600, 700, 800, 900, 950];

function get_color_scheme(color: string) {
    return Object.fromEntries(
        shades.map( (shade: number) => [shade, `{${color}.${shade}}`])
    )
}

export const AppThemes = {
    emerald: get_color_scheme('emerald'),
    green: get_color_scheme('green'),
    lime: get_color_scheme('lime'),
    red: get_color_scheme('red'),
    orange: get_color_scheme('orange'),
    amber: get_color_scheme('amber'),
    yellow: get_color_scheme('yellow'),
    teal: get_color_scheme('teal'),
    cyan: get_color_scheme('cyan'),
    sky: get_color_scheme('sky'),
    blue: get_color_scheme('blue'),
    indigo: get_color_scheme('indigo'),
    violet: get_color_scheme('violet'),
    purple: get_color_scheme('purple'),
    fuchsia: get_color_scheme('fuchsia'),
    pink: get_color_scheme('pink'),
    rose: get_color_scheme('rose'),
}

export const AppThemePreset = definePreset(Aura, {
    semantic: {
        colorScheme: {
            light: {
                primary: AppThemes.blue,
                surface: {
                    0: '#ffffff',
                    ...get_color_scheme('zinc'),
                }
            },
            dark: {
                primary: AppThemes.blue,
                surface: {
                    0: '#ffffff',
                    ...get_color_scheme('slate'),
                }
            }
        }
    }
});

