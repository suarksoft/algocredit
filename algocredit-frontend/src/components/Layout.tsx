'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import clsx from 'clsx'

import { Hero } from '@/components/Hero'
import { Logo, Logomark } from '@/components/Logo'
import { MobileNavigation } from '@/components/MobileNavigation'
import { Navigation } from '@/components/Navigation'
import { ThemeSelector } from '@/components/ThemeSelector'
import { WalletStatus } from '@/components/WalletConnect'

// Wallet icon for header
function WalletIcon(props: React.ComponentPropsWithoutRef<'svg'>) {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" {...props}>
      <path d="M21 7.5V6a2 2 0 00-2-2H5a2 2 0 00-2 2v1.5m18 0A1.5 1.5 0 0022.5 9v6a1.5 1.5 0 01-1.5 1.5H3A1.5 1.5 0 011.5 15V9A1.5 1.5 0 013 7.5m18 0V9a1.5 1.5 0 01-1.5 1.5h-9A1.5 1.5 0 019 9v-.5m0 0V6a2 2 0 012-2h2a2 2 0 012 2v1.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  )
}

// GitHub icon for footer
function GitHubIcon(props: React.ComponentPropsWithoutRef<'svg'>) {
  return (
    <svg aria-hidden="true" viewBox="0 0 16 16" {...props}>
      <path d="M8 0C3.58 0 0 3.58 0 8C0 11.54 2.29 14.53 5.47 15.59C5.87 15.66 6.02 15.42 6.02 15.21C6.02 15.02 6.01 14.39 6.01 13.72C4 14.09 3.48 13.23 3.32 12.78C3.23 12.55 2.84 11.84 2.5 11.65C2.22 11.5 1.82 11.13 2.49 11.12C3.12 11.11 3.57 11.7 3.72 11.94C4.44 13.15 5.59 12.81 6.05 12.6C6.12 12.08 6.33 11.73 6.56 11.53C4.78 11.33 2.92 10.64 2.92 7.58C2.92 6.71 3.23 5.99 3.74 5.43C3.66 5.23 3.38 4.41 3.82 3.31C3.82 3.31 4.49 3.1 6.02 4.13C6.66 3.95 7.34 3.86 8.02 3.86C8.7 3.86 9.38 3.95 10.02 4.13C11.55 3.09 12.22 3.31 12.22 3.31C12.66 4.41 12.38 5.23 12.3 5.43C12.81 5.99 13.12 6.7 13.12 7.58C13.12 10.65 11.25 11.33 9.47 11.53C9.76 11.78 10.01 12.26 10.01 13.01C10.01 14.08 10 14.94 10 15.21C10 15.42 10.15 15.67 10.55 15.59C13.71 14.53 16 11.53 16 8C16 3.58 12.42 0 8 0Z" />
    </svg>
  )
}

function Header() {
  let [isScrolled, setIsScrolled] = useState(false)
  let pathname = usePathname()

  useEffect(() => {
    function onScroll() {
      setIsScrolled(window.scrollY > 0)
    }
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => {
      window.removeEventListener('scroll', onScroll)
    }
  }, [])

  const navItems = [
    { name: 'Home', href: '/' },
    { name: 'Apply', href: '/apply' },
    { name: 'Dashboard', href: '/dashboard' },
    { name: 'How it Works', href: '/how-it-works' },
  ]

  return (
    <header
      className={clsx(
        'sticky top-0 z-50 flex flex-none flex-wrap items-center justify-between bg-white px-4 py-4 shadow-md shadow-slate-900/5 transition duration-500 sm:px-6 lg:px-8 dark:shadow-none',
        isScrolled
          ? 'dark:bg-slate-900/95 dark:backdrop-blur-sm dark:[@supports(backdrop-filter:blur(0))]:bg-slate-900/75'
          : 'dark:bg-transparent',
      )}
    >
      {/* Mobile menu button */}
      <div className="mr-6 flex lg:hidden">
        <MobileNavigation />
      </div>

      {/* Logo */}
      <div className="relative flex items-center">
        <Link href="/" aria-label="AlgoCredit Home">
          <Logomark className="h-8 w-8 lg:hidden" />
          <Logo className="hidden h-8 w-auto fill-slate-700 lg:block dark:fill-sky-100" />
        </Link>
      </div>

      {/* Desktop Navigation */}
      <nav className="hidden lg:flex lg:items-center lg:space-x-8">
        {navItems.map((item) => (
          <Link
            key={item.name}
            href={item.href}
            className={clsx(
              'text-sm font-medium transition-colors hover:text-blue-600 dark:hover:text-blue-400',
              pathname === item.href
                ? 'text-blue-600 dark:text-blue-400'
                : 'text-slate-700 dark:text-slate-300'
            )}
          >
            {item.name}
          </Link>
        ))}
      </nav>

      {/* Right side - Theme + Wallet */}
      <div className="flex items-center gap-4">
        <ThemeSelector className="relative z-10" />
        <WalletStatus />
      </div>
    </header>
  )
}

export function Layout({ children }: { children: React.ReactNode }) {
  let pathname = usePathname()
  let isHomePage = pathname === '/'

  return (
    <div className="flex w-full flex-col">
      <Header />

      {isHomePage && <Hero />}

      <div className="relative mx-auto flex w-full max-w-8xl flex-auto justify-center sm:px-2 lg:px-8 xl:px-12">
        <div className="lg:relative lg:block lg:flex-none">
          <div className="absolute inset-y-0 right-0 w-[50vw] bg-slate-50 dark:hidden" />
          <div className="absolute top-16 right-0 bottom-0 hidden h-12 w-px bg-linear-to-t from-slate-800 dark:block" />
          <div className="absolute top-28 right-0 bottom-0 hidden w-px bg-slate-800 dark:block" />
          <div className="sticky top-19 -ml-0.5 h-[calc(100vh-4.75rem)] w-64 overflow-x-hidden overflow-y-auto py-16 pr-8 pl-0.5 xl:w-72 xl:pr-16">
            <Navigation />
          </div>
        </div>
        {children}
      </div>
    </div>
  )
}
