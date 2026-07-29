import type { Configuration } from '@azure/msal-browser'
import { PublicClientApplication } from '@azure/msal-browser'

const CLIENT_ID = '89a89132-cc9d-4492-ac67-1c4b54f37932'
const TENANT_ID = '3c6322bf-c349-48f5-bdc9-750baa5c79a8'

export const msalConfig: Configuration = {
  auth: {
    clientId: CLIENT_ID,
    authority: `https://login.microsoftonline.com/${TENANT_ID}`,
    // Must match the redirect URIs registered in Azure AD exactly
    redirectUri: `${window.location.origin}/auth/callback`,
    postLogoutRedirectUri: window.location.origin,
  },
  cache: {
    cacheLocation: 'sessionStorage', // sessionStorage is more secure than localStorage
  },
}

export const loginRequest = {
  scopes: ['openid', 'profile', 'email'],
}

export const msalInstance = new PublicClientApplication(msalConfig)

/** Returns the current user's ID token, or null if not signed in. */
export async function getIdToken(): Promise<string | null> {
  const accounts = msalInstance.getAllAccounts()
  if (accounts.length === 0) return null
  try {
    const result = await msalInstance.acquireTokenSilent({
      ...loginRequest,
      account: accounts[0],
    })
    return result.idToken
  } catch {
    return null
  }
}
