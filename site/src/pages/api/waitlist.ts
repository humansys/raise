import type { APIRoute } from 'astro';

export const prerender = false;

interface WaitlistRequest {
  email: string;
  tier: 'pro' | 'enterprise';
  company?: string;
  website?: string; // honeypot field
}

interface WaitlistResponse {
  ok: boolean;
  message: string;
}

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const JIRA_BASE_URL = 'https://humansys.atlassian.net';
const JIRA_PROJECT_KEY = 'LEADS';
const RESEND_API_URL = 'https://api.resend.com/emails';

interface CreateJiraContactParams {
  email: string;
  tier: string;
  company: string;
  jiraEmail: string;
  jiraToken: string;
}

interface JiraIssueResponse {
  key: string;
  id: string;
}

async function createJiraContact(params: CreateJiraContactParams): Promise<JiraIssueResponse> {
  const { email, tier, company, jiraEmail, jiraToken } = params;

  const summary = `${email} — ${tier.charAt(0).toUpperCase() + tier.slice(1)}`;
  const description = {
    type: 'doc',
    version: 1,
    content: [
      {
        type: 'paragraph',
        content: [
          {
            type: 'text',
            text: `Email: ${email}\nTier: ${tier}\nCompany: ${company || 'N/A'}\nSource: pricing page\nDate: ${new Date().toISOString().split('T')[0]}`,
          },
        ],
      },
    ],
  };

  const auth = btoa(`${jiraEmail}:${jiraToken}`);

  const response = await fetch(`${JIRA_BASE_URL}/rest/api/3/issue`, {
    method: 'POST',
    headers: {
      Authorization: `Basic ${auth}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      fields: {
        project: { key: JIRA_PROJECT_KEY },
        issuetype: { name: 'Contact' },
        summary,
        description,
      },
    }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Jira API error: ${response.status} ${errorText}`);
  }

  return response.json();
}

interface SendConfirmationEmailParams {
  email: string;
  tier: string;
  resendApiKey: string;
}

async function sendConfirmationEmail(params: SendConfirmationEmailParams): Promise<void> {
  const { email, tier, resendApiKey } = params;

  const tierName = tier.charAt(0).toUpperCase() + tier.slice(1);
  const nextSteps =
    tier === 'enterprise'
      ? "- Enterprise: I'll reach out personally within 24 hours\n  to learn about your use case."
      : "- Pro: You'll hear from me when we're ready for early access.";

  const textContent = `Hi,

You're on the waitlist for RaiSE ${tierName}.

What happens next:
${nextSteps}

While you wait, explore the framework:
- Docs: https://raiseframework.ai/docs/
- Getting Started: https://raiseframework.ai/docs/getting-started/

— Emilio
Founder, RaiSE Framework`;

  const response = await fetch(RESEND_API_URL, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${resendApiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      from: 'Emilio Guardia <emilio@humansys.ai>',
      to: [email],
      subject: "You're on the RaiSE waitlist",
      text: textContent,
    }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Resend API error: ${response.status} ${errorText}`);
  }
}

export const POST: APIRoute = async ({ request, locals }) => {
  const runtime = locals.runtime as { env: Env };
  const db = runtime.env.DB;

  try {
    const body = await request.json() as WaitlistRequest;

    // Honeypot check — if filled, silently discard
    if (body.website && body.website.trim() !== '') {
      console.log('[Honeypot] Bot detected, discarding silently');
      return new Response(
        JSON.stringify({
          ok: true,
          message: "You're on the list. We'll be in touch.",
        } satisfies WaitlistResponse),
        { status: 200, headers: { 'Content-Type': 'application/json' } }
      );
    }

    // Validate email
    const email = body.email?.trim().toLowerCase();
    if (!email || !EMAIL_REGEX.test(email)) {
      return new Response(
        JSON.stringify({
          ok: false,
          message: 'Please provide a valid email address.',
        } satisfies WaitlistResponse),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    // Validate tier
    if (!body.tier || !['pro', 'enterprise'].includes(body.tier)) {
      return new Response(
        JSON.stringify({
          ok: false,
          message: 'Please select a valid tier.',
        } satisfies WaitlistResponse),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const company = body.company?.trim() || '';

    // Insert into D1 (idempotent — ON CONFLICT IGNORE)
    const result = await db
      .prepare(`
        INSERT INTO waitlist (email, tier, company, source, status)
        VALUES (?, ?, ?, 'pricing', 'new')
        ON CONFLICT(email) DO NOTHING
      `)
      .bind(email, body.tier, company)
      .run();

    // Check if it was a duplicate (changes === 0)
    const isDuplicate = result.meta.changes === 0;

    if (isDuplicate) {
      console.log(`[Duplicate] Email ${email} already on waitlist`);
    } else {
      console.log(`[Success] New lead: ${email} (${body.tier})`);

      // Only create Jira issue + send email for NEW leads (not duplicates)
      let jiraIssueKey: string | null = null;

      // Best-effort: Create Jira Contact issue
      try {
        const jiraResponse = await createJiraContact({
          email,
          tier: body.tier,
          company,
          jiraEmail: runtime.env.JIRA_EMAIL,
          jiraToken: runtime.env.JIRA_API_TOKEN,
        });
        jiraIssueKey = jiraResponse.key;
        console.log(`[Jira] Created issue: ${jiraIssueKey}`);

        // Store Jira issue key back in D1
        await db
          .prepare('UPDATE waitlist SET jira_issue_key = ? WHERE email = ?')
          .bind(jiraIssueKey, email)
          .run();
      } catch (error) {
        console.error('[Jira] Failed to create issue:', error);
        // Continue — lead is safe in D1
      }

      // Best-effort: Send confirmation email
      try {
        await sendConfirmationEmail({
          email,
          tier: body.tier,
          resendApiKey: runtime.env.RESEND_API_KEY,
        });
        console.log(`[Resend] Confirmation email sent to ${email}`);
      } catch (error) {
        console.error('[Resend] Failed to send email:', error);
        // Continue — lead is safe in D1 + Jira
      }
    }

    // Always return success (idempotent)
    return new Response(
      JSON.stringify({
        ok: true,
        message: "You're on the list. We'll be in touch.",
      } satisfies WaitlistResponse),
      { status: 200, headers: { 'Content-Type': 'application/json' } }
    );
  } catch (error) {
    console.error('[Error] Waitlist endpoint failed:', error);
    return new Response(
      JSON.stringify({
        ok: false,
        message: 'Something went wrong. Please try again later.',
      } satisfies WaitlistResponse),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
};
