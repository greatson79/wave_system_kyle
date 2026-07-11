import { toPng } from 'html-to-image'

export async function downloadElementAsImage(element: HTMLElement, filename: string) {
  const dataUrl = await toPng(element, {
    pixelRatio: 2,
    backgroundColor: '#ffffff',
  })
  const link = document.createElement('a')
  link.download = filename
  link.href = dataUrl
  link.click()
}
