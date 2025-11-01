# Security Policy

## 🔒 Reporting Security Vulnerabilities

If you discover a security vulnerability in PrepSmart, please report it responsibly:

1. **DO NOT** open a public GitHub issue
2. Email the maintainer through GitHub (see profile)
3. Include detailed steps to reproduce the vulnerability
4. Allow up to 48 hours for initial response

## 🛡️ Security Best Practices for Users

### API Key Protection

**CRITICAL**: Your Claude API key is sensitive and should NEVER be committed to version control.

✅ **DO**:
- Store API keys in `.env` files (already in `.gitignore`)
- Use environment variables for all secrets
- Rotate API keys if accidentally exposed
- Use different API keys for development and production
- Monitor your API usage at https://console.anthropic.com/

❌ **DON'T**:
- Commit `.env` files to git
- Share API keys in screenshots or documentation
- Hardcode API keys in source code
- Store API keys in frontend JavaScript
- Share your `.env` file with others

### If You Accidentally Commit an API Key

1. **Immediately rotate the key** at https://console.anthropic.com/
2. Remove the key from git history:
   ```bash
   # Use BFG Repo Cleaner or git filter-branch
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch backend/.env" \
     --prune-empty --tag-name-filter cat -- --all
   ```
3. Force push to remote (if already pushed):
   ```bash
   git push origin --force --all
   ```
4. Update your local `.env` with the new key

### Environment Setup Security

When setting up PrepSmart:

1. **Never use example API keys** in production
2. **Generate strong Flask secret keys**:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
3. **Use HTTPS** in production (Azure Container Apps provides this)
4. **Limit CORS origins** to only your frontend domain
5. **Set `FLASK_DEBUG=False`** in production

### Production Deployment Security

For Azure Container Apps:

1. **Use Azure Key Vault** for secrets (optional advanced setup)
2. **Enable HTTPS only** (disable HTTP)
3. **Set environment variables** through Azure Portal, not in Dockerfile
4. **Use managed identities** when possible
5. **Monitor API usage** to detect abuse

### Database Security

- SQLite is used for development only
- For production, consider PostgreSQL with encryption
- Never commit `.db` files to git (already in `.gitignore`)
- Regularly backup production databases

### User Data Privacy

PrepSmart follows these privacy principles:

✅ **We DO**:
- Store crisis plans only during active sessions
- Use data solely for generating personalized plans
- Allow users to download their plans
- Clear session data after completion

❌ **We DON'T**:
- Sell user data to third parties
- Share personal information with external services (except Claude API for processing)
- Track users across sessions
- Store credit card or payment information

## 🔍 What's Protected

### Already Secured

- ✅ `.env` files in `.gitignore`
- ✅ API keys removed from documentation
- ✅ Database files excluded from git
- ✅ Python bytecode and caches ignored
- ✅ Environment variable templates provided

### User Responsibility

- 🔑 Keeping your Claude API key secret
- 🔐 Generating secure Flask secret keys
- 🌐 Configuring production CORS properly
- 💰 Monitoring your API usage and costs

## 📋 Security Checklist for Contributors

Before submitting a PR:

- [ ] No API keys or secrets in code
- [ ] No hardcoded credentials
- [ ] `.env` files not committed
- [ ] Sensitive data not in screenshots
- [ ] Dependencies up to date
- [ ] No SQL injection vulnerabilities
- [ ] Input validation implemented
- [ ] CORS configured properly
- [ ] Error messages don't leak sensitive info

## 🚨 Known Limitations

- SQLite is not recommended for high-concurrency production use
- No rate limiting implemented (rely on Claude API's limits)
- Session storage is in-memory (not persistent)
- No built-in API authentication (frontend is public)

For production deployments, consider:
- Adding rate limiting middleware
- Implementing user authentication
- Using PostgreSQL or similar database
- Adding request logging and monitoring

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/latest/security/)
- [Anthropic API Security](https://docs.anthropic.com/en/api/security)
- [Azure Security Best Practices](https://learn.microsoft.com/en-us/azure/security/)

## 📅 Last Updated

2025-01-XX - Initial security policy

---

**Remember**: Security is a shared responsibility. Stay vigilant and report issues promptly!
