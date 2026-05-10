export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  tool?: string
}

export async function sendMessage(message: string, signal?: AbortSignal): Promise<ChatMessage> {
  const res = await fetch('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
    signal,
  })
  if (!res.ok) throw new Error(await res.text())
  const data = await res.json()
  return data.message
}

export async function cancelChat(): Promise<void> {
  await fetch('/cancel', { method: 'POST' })
}
