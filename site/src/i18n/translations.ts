export const ui = {
  en: {
    'nav.framework': 'Framework',
    'nav.docs': 'Docs',
    'nav.pricing': 'Pricing',
    'nav.blog': 'Blog',
    'nav.github': 'GitHub',
    'nav.lang.switch': 'ES',
    'nav.lang.label': 'Cambiar a español',
    'footer.docs': 'Docs',
    'footer.blog': 'Blog',
    'footer.github': 'GitHub',
    'meta.description':
      'A lean methodology and deterministic toolkit for reliable AI-assisted software engineering.',
  },
  es: {
    'nav.framework': 'Framework',
    'nav.docs': 'Docs',
    'nav.pricing': 'Precios',
    'nav.blog': 'Blog',
    'nav.github': 'GitHub',
    'nav.lang.switch': 'EN',
    'nav.lang.label': 'Switch to English',
    'footer.docs': 'Docs',
    'footer.blog': 'Blog',
    'footer.github': 'GitHub',
    'meta.description':
      'Una metodología lean y toolkit determinístico para ingeniería de software confiable asistida por IA.',
  },
} as const;

export type TranslationKey = keyof (typeof ui)['en'];
