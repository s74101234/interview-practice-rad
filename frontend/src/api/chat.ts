export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  tool?: string
}

export async function sendMessage(message: string): Promise<ChatMessage> {
  const res = await fetch('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  })
  if (!res.ok) throw new Error(await res.text())
  const data = await res.json()
  return data.message
}
