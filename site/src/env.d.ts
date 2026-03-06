/// <reference path="../.astro/types.d.ts" />
/// <reference types="astro/client" />

type Runtime = import("@astrojs/cloudflare").Runtime<Env>;

declare namespace App {
  interface Locals extends Runtime {
    // Cloudflare runtime with D1 binding
  }
}

interface Env {
  DB: D1Database;
  RESEND_API_KEY: string;
  JIRA_EMAIL: string;
  JIRA_API_TOKEN: string;
}
