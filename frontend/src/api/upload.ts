export async function uploadFile(file: File): Promise<{ job_id: string; filename: string }> {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch('/upload', { method: 'POST', body: form })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}
