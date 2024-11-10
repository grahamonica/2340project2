import { Header } from '@/app/components/layout/Header'
import { ThemeProvider } from 'next-themes'
import './globals.css'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head />
      <body>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <div className="min-h-screen bg-white dark:bg-gray-900 text-black dark:text-white">
            <Header />
            {children}
          </div>
        </ThemeProvider>
      </body>
    </html>
  )
}