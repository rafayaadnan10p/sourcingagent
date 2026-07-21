import { createContext, useContext, useState, type ReactNode } from 'react'

interface SearchContextValue {
  isSearching: boolean
  setIsSearching: (v: boolean) => void
}

const SearchContext = createContext<SearchContextValue>({
  isSearching: false,
  setIsSearching: () => {},
})

export function SearchProvider({ children }: { children: ReactNode }) {
  const [isSearching, setIsSearching] = useState(false)
  return (
    <SearchContext.Provider value={{ isSearching, setIsSearching }}>
      {children}
    </SearchContext.Provider>
  )
}

export const useSearchContext = () => useContext(SearchContext)


