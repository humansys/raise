// @ts-check
import { defineConfig } from 'astro/config';
import cloudflare from '@astrojs/cloudflare';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import starlight from '@astrojs/starlight';
import starlightLlmsTxt from 'starlight-llms-txt';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  site: 'https://raiseframework.ai',
  output: 'static',
  adapter: cloudflare(),
  // i18n is configured by Starlight's locales (cannot coexist with Astro i18n block).
  // Our custom pages use src/i18n/utils.ts which parses URLs directly.
  integrations: [
    starlight({
      title: 'RaiSE Docs',
      logo: {
        src: './public/logo.svg',
        alt: 'RaiSE Framework',
      },
      customCss: [
        './src/styles/starlight.css',
      ],
      disable404Route: true,
      defaultLocale: 'root',
      locales: {
        root: { label: 'English', lang: 'en' },
        es: { label: 'Español', lang: 'es' },
      },
      sidebar: [
        {
          label: 'Start Here',
          translations: { es: 'Comienza Aquí' },
          items: [
            { slug: 'docs' },
            { slug: 'docs/getting-started' },
          ],
        },
        {
          label: 'Concepts',
          translations: { es: 'Conceptos' },
          items: [
            { slug: 'docs/concepts/memory' },
            { slug: 'docs/concepts/skills' },
            { slug: 'docs/concepts/governance' },
            { slug: 'docs/concepts/knowledge-graph' },
          ],
        },
        {
          label: 'Guides',
          translations: { es: 'Guías' },
          items: [
            { slug: 'docs/guides/first-story' },
            { slug: 'docs/guides/setting-up' },
          ],
        },
        {
          label: 'Reference',
          translations: { es: 'Referencia' },
          items: [
            { slug: 'docs/cli' },
          ],
        },
      ],
      plugins: [
        starlightLlmsTxt({
          projectName: 'RaiSE Framework',
          description:
            'A lean methodology and deterministic toolkit for reliable AI-assisted software engineering.',
        }),
      ],
    }),
    mdx(),
    sitemap(),
  ],
  vite: {
    plugins: [tailwindcss()],
  },
});
