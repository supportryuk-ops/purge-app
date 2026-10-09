# Purge (Gmail Wipe web app)

Static page `index.html`: signs in with Google in the browser and calls the Gmail API directly. No backend.
(`cli/gmail_wipe.py` is the equivalent local CLI; run `pip install -r cli/requirements.txt` first.)

## 1. Google Cloud setup
1. console.cloud.google.com -> create a project -> enable **Gmail API**.
2. OAuth consent screen: User type External (or Internal for Workspace). Add your account under **Test users**.
3. Credentials -> Create **OAuth client ID** -> type **Web application**.
   - Authorized JavaScript origins: `http://localhost:8000` and your deployed URL
     (e.g. `https://your-site.netlify.app` / `https://your-site.vercel.app`).
4. Copy the Client ID into `CLIENT_ID` in `index.html`.

## 2. Test locally
    python -m http.server 8000     # then open http://localhost:8000

## 3. Deploy
- Netlify: drag the `gmail-wipe` folder onto app.netlify.com/drop, or `netlify deploy --prod --dir .`
- Vercel: `npx vercel --prod` from this folder (framework: Other, no build).

Add the final URL to the OAuth client's authorized origins (step 1.3).

## Notes
- First sign-in shows "Google hasn't verified this app": Advanced -> Continue (fine for personal use as a test user).
- Test-mode tokens/consent expire after 7 days; just sign in again.
- Prefer "Move to Trash" first. Permanent delete is irreversible.
- Consider protecting the deployed URL (Netlify/Vercel password protection) or taking it down after use.
