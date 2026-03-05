// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://docs.raiseframework.ai',
  output: 'static',
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
            { slug: 'docs/concepts' },
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
            { slug: 'docs/guides/extending' },
            { slug: 'docs/guides/create-adapter' },
            { slug: 'docs/guides/create-skill' },
            { slug: 'docs/guides/register-mcp' },
            { slug: 'docs/guides/create-hook' },
          ],
        },
        {
          label: 'Reference',
          translations: { es: 'Referencia' },
          items: [
            { slug: 'docs/cli' },
            { slug: 'docs/cli/init' },
            { slug: 'docs/cli/session' },
            { slug: 'docs/cli/graph' },
            { slug: 'docs/cli/pattern' },
            { slug: 'docs/cli/signal' },
            { slug: 'docs/cli/backlog' },
            { slug: 'docs/cli/skill' },
            { slug: 'docs/cli/discover' },
            { slug: 'docs/cli/adapter' },
            { slug: 'docs/cli/mcp' },
            { slug: 'docs/cli/gate' },
            { slug: 'docs/cli/doctor' },
            { slug: 'docs/cli/docs' },
            { slug: 'docs/cli/artifact' },
            { slug: 'docs/cli/release' },
            { slug: 'docs/cli/info' },
            { slug: 'docs/cli/profile' },
          ],
        },
      ],
    }),
  ],
});
