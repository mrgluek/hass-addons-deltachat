# Delta Chat Publish Bot (`deltachat_publish`)

`deltachat_publish` is a Delta Chat bot designed to publish new blog posts and attached image assets directly to an Astro blog (`gluek.info` or any Astro theme like Astro Nano) via the Forgejo / Gitea REST API.

Following **IndieWeb / POSSE** principles, your Git repository remains the single source of truth.

## Key Features

- **Single-Commit Multi-File API Publishing**: Uses Forgejo `ChangeFilesOptions` REST API to create both the post Markdown file (`.md`) and attached images in a **single API request / single Git commit**.
- **100% CI/CD Efficient**: Triggers your Forgejo Actions build pipeline only **once** per post creation.
- **Flexible Astro Layout Support**:
  - `single_file` layout (`gluek.info`): Post in `src/content/blog/<slug>.md`, images in `public/images/<slug>/`.
  - `folder` layout (`Astro Nano`): Post in `src/content/blog/<slug>/index.md`, images alongside in `src/content/blog/<slug>/`.
- **Automatic Slugification**: Transliterates Russian titles to clean URL slugs (e.g. `Мой новый пост` → `moy-novyy-post`).
- **End-to-End Encryption (E2EE)**: All communication between your Delta Chat client and the bot is encrypted using OpenPGP / Autocrypt.
- **Cryptographic Fingerprint & Email Verification**: The bot strictly verifies the sender's email AND cryptographic OpenPGP fingerprint against authorized administrators.

## Configuration

In the **Configuration** tab:

1. **Account Credentials**:
   - `chatmail_qr`: Paste your Chatmail QR string (`DCACCOUNT:...`) or URI for instant 1-click account setup.
   - Or `email` and `password`: Standard IMAP/SMTP credentials.
2. **Forgejo / Gitea REST API Settings**:
   - `forgejo_url`: URL of your Forgejo/Gitea instance (e.g. `https://git.gluek.info`).
   - `forgejo_token`: Personal access token generated in Forgejo (*Settings -> Applications -> Generate New Token* with `repo` scope).
   - `forgejo_repo_owner`: Repository owner/organization (e.g. `gluek`).
   - `forgejo_repo_name`: Repository name (e.g. `gluek.info`).
   - `forgejo_branch`: Target branch (default: `main`).
3. **Astro Blog Layout**:
   - `blog_post_format`: Layout format (`single_file` or `folder`).
   - `blog_content_path`: Content path in git repo (default: `src/content/blog`).
   - `blog_images_path`: Images path in git repo (default: `public/images`).
   - `blog_image_url_prefix`: Image URL path prefix in Markdown (default: `/images`).
   - `blog_public_url_prefix`: Public blog URL for post link replies (e.g. `https://gluek.info/blog`).
4. **Admin Security**:
   - `admin_email`: Your Delta Chat email address authorized to publish posts.
   - `admin_fingerprint`: Optional cryptographic OpenPGP fingerprint.

## How to Publish a Post

Simply send a chat message to your bot in Delta Chat:

```text
Title of Your Post

This is the body of the post in Markdown format.
You can write multiple paragraphs.

[Attach photo(s) or file(s)]
```

The bot will:
1. Extract Title from Line 1.
2. Transliterate Title into a clean URL slug.
3. Automatically trim the first 150 characters of the body for the YAML `description`.
4. Upload all attached photos and insert Markdown image tags `![filename](path)` automatically.
5. Create a single commit via Forgejo API and reply with success confirmation & commit link!
