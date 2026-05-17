# Content CTR Factory

Content CTR Factory is a mock-only module that helps marketplace managers create main-photo content hypotheses and connect them to CTR tests. It does not generate real images and does not publish card content.

## Content Brief

The brief contains:

- `marketplace`
- `sku`
- `product_name`
- `category`
- `target_audience`
- `buyer_pains`
- `key_features`
- `competitor_references`
- `current_ctr`
- `target_ctr`

## Hypothesis Generator

The factory creates 5–10 hypotheses for the main photo. Each hypothesis includes:

- idea;
- why it may work;
- which buyer pain it addresses;
- which element should be tested;
- risk level.

## Prompt Generator

For selected hypotheses the module creates image-generation prompts:

- Sora prompt;
- GPT image prompt;
- Midjourney/other generator prompt;
- English prompt text;
- separate Russian text blocks for overlays.

## CTR Test Plan

The test plan includes:

- what is tested;
- success metric;
- test period;
- minimum traffic;
- winner criteria.

## Safety

- Content is never published automatically.
- All card changes are draft-only.
- Publication requires approval.
- Bulk content changes require hard approval.
- All data and prompts are mock-only.

## API endpoints

- `POST /content/brief`
- `POST /content/hypotheses`
- `POST /content/prompts`
- `GET /content/sku/{sku}`

## Telegram commands

- `/content_sku <sku>`
- `/ctr_test`
- `/content_brief`
