import { ui, type TranslationKey } from './translations';
import { defaultLocale, locales, type Locale } from './config';

/** Extract locale from URL pathname. Returns defaultLocale if not found. */
export function getLocaleFromUrl(url: URL): Locale {
  const [, segment] = url.pathname.split('/');
  if (locales.includes(segment as Locale)) return segment as Locale;
  return defaultLocale;
}

/** Build a localized path. Default locale gets no prefix. */
export function getLocalizedPath(path: string, locale: Locale): string {
  const clean = path.startsWith('/') ? path : `/${path}`;
  if (locale === defaultLocale) return clean;
  return `/${locale}${clean}`;
}

/** Get the equivalent path in the other locale (for language switcher). */
export function getSwitchLocalePath(url: URL): string {
  const currentLocale = getLocaleFromUrl(url);
  const targetLocale = currentLocale === 'en' ? 'es' : 'en';

  if (currentLocale === defaultLocale) {
    // English → Spanish: prepend /es
    return `/${targetLocale}${url.pathname}`;
  }
  // Spanish → English: strip /es prefix
  const stripped = url.pathname.replace(`/${currentLocale}`, '') || '/';
  return stripped;
}

/** Translate a UI string key for the given locale. */
export function t(key: TranslationKey, locale: Locale): string {
  return ui[locale][key] ?? ui[defaultLocale][key];
}
