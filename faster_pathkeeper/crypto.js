// Crypto utilities for Pathkeeper

export async function encryptData(passphrase, data) {
  const encoder = new TextEncoder();
  const dataStr = JSON.stringify(data);
  const dataBuffer = encoder.encode(dataStr);
  
  // Simple encryption using Web Crypto API
  const keyMaterial = await crypto.subtle.importKey(
    'raw',
    encoder.encode(passphrase),
    { name: 'PBKDF2' },
    false,
    ['deriveBits', 'deriveKey']
  );
  
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const key = await crypto.subtle.deriveKey(
    {
      name: 'PBKDF2',
      salt: salt,
      iterations: 100000,
      hash: 'SHA-256'
    },
    keyMaterial,
    { name: 'AES-GCM', length: 256 },
    false,
    ['encrypt']
  );
  
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const encryptedData = await crypto.subtle.encrypt(
    { name: 'AES-GCM', iv: iv },
    key,
    dataBuffer
  );
  
  // Combine salt, iv, and encrypted data
  const combined = new Uint8Array(salt.length + iv.length + encryptedData.byteLength);
  combined.set(salt, 0);
  combined.set(iv, salt.length);
  combined.set(new Uint8Array(encryptedData), salt.length + iv.length);
  
  // Convert to base64 string for storage
  return btoa(String.fromCharCode(...combined));
}

export async function decryptData(passphrase, encryptedStr) {
  const encoder = new TextEncoder();
  const decoder = new TextDecoder();
  
  // Convert from base64
  const combined = Uint8Array.from(atob(encryptedStr), c => c.charCodeAt(0));
  
  // Extract salt, iv, and encrypted data
  const salt = combined.slice(0, 16);
  const iv = combined.slice(16, 28);
  const encryptedData = combined.slice(28);
  
  const keyMaterial = await crypto.subtle.importKey(
    'raw',
    encoder.encode(passphrase),
    { name: 'PBKDF2' },
    false,
    ['deriveBits', 'deriveKey']
  );
  
  const key = await crypto.subtle.deriveKey(
    {
      name: 'PBKDF2',
      salt: salt,
      iterations: 100000,
      hash: 'SHA-256'
    },
    keyMaterial,
    { name: 'AES-GCM', length: 256 },
    false,
    ['decrypt']
  );
  
  const decryptedData = await crypto.subtle.decrypt(
    { name: 'AES-GCM', iv: iv },
    key,
    encryptedData
  );
  
  const dataStr = decoder.decode(decryptedData);
  return JSON.parse(dataStr);
}
