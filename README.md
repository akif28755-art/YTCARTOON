# Cartoon Cloud Starter (v1)

A **working starter renderer** for a children's cartoon, designed for GitHub Actions. No CMD, Python or FFmpeg installation on your Windows PC. All processing runs on GitHub's Linux runner.

## Browser-only setup
1. Sign in at https://github.com and create a **private** repository.
2. Choose **Add file > Upload files**, and upload `render.py`, `stories/story.json`, and `.github/workflows/create-video.yml` preserving folders. GitHub's browser uploader may not preserve hidden folder paths; use **Add file > Create new file** and type `.github/workflows/create-video.yml` as the filename if necessary.
3. Open **Actions > Create children's cartoon > Run workflow**.
4. Wait for the job to finish. Open the job run and download the `cartoon-video` artifact. Unzip to get `cartoon.mp4` and `youtube_metadata.json`.
5. Edit `stories/story.json` in the GitHub browser to change the story, scene backgrounds and subtitles, then rerun.

## What actually works
- 1280x720 MP4 with moving, hand-drawn-style 2D cartoon characters, scene changes, subtitles and English speech.
- Attempts Microsoft Edge online neural voice via `edge-tts`; falls back to offline `espeak-ng` if unavailable. Voice quality is **not guaranteed**.
- Runs in the cloud after you close the browser or shut down your PC (subject to GitHub Actions availability and usage limits).
- Original example children's story with three short scenes.

## Important limitations
- **Not AI-generated animation**: backgrounds and characters are procedurally drawn templates; scenes are selected from `place` in the JSON. This is not Pixar-level animation or generative video.
- **No automatic new story generation**: you supply/edit story JSON. No paid AI API is used.
- **No automatic YouTube upload** in this starter: YouTube OAuth needs secure account authorization and configuration. Upload via YouTube Studio. Mark appropriately as made for kids; YouTube Kids inclusion is not guaranteed.
- The example is short (~1 minute); 10–120 minute production is NOT validated and may exceed free compute/storage limits. A selected duration alone cannot create meaningful long stories.
- No ongoing cost is promised; GitHub's free quotas, policies and terms may change.
- Review every video before publishing, especially for children. Do not put private OAuth tokens in a public repository.
