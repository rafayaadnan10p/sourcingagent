import api from './client'

export interface SearchResult {
  id: string
  url: string
  title: string | null
  snippet: string | null
  original_position: number
  relevance_score: number | null
  relevance_reasoning: string | null
  final_rank: number | null
  is_starred: boolean
  is_recruited: boolean
  created_at: string
}

export interface Search {
  id: string
  jd_text: string
  jd_filename: string | null
  search_strings: { label: string; query: string }[] | null
  platform_scope: string
  created_at: string
  results: SearchResult[]
}

export interface SearchSummary {
  id: string
  title: string
  jd_preview: string
  platform_scope: string
  created_at: string
  result_count: number
}

export const runSearch = async (
  jdText: string,
  platformScope: string,
  locationOverride: string = 'not_specified',
  targetCompanies: string = '',
  openToWork: boolean = false,
): Promise<Search> => {
  const { data } = await api.post('/search', {
    jd_text: jdText,
    platform_scope: platformScope,
    location_override: locationOverride,
    target_companies: targetCompanies,
    open_to_work: openToWork,
  })
  return data
}

export const uploadJD = async (file: File): Promise<{ jd_text: string; filename: string }> => {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post('/jd/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export const listSearches = async (): Promise<SearchSummary[]> => {
  const { data } = await api.get('/searches')
  return data
}

export const getSearch = async (id: string): Promise<Search> => {
  const { data } = await api.get(`/searches/${id}`)
  return data
}

export const toggleStar = async (resultId: string): Promise<SearchResult> => {
  const { data } = await api.patch(`/results/${resultId}/star`)
  return data
}

export const toggleRecruit = async (resultId: string): Promise<SearchResult> => {
  const { data } = await api.patch(`/results/${resultId}/recruit`)
  return data
}

export const deleteSearch = async (id: string): Promise<void> => {
  await api.delete(`/searches/${id}`)
}

export const getStarred = async (): Promise<SearchResult[]> => {
  const { data } = await api.get('/results/starred')
  return data
}

export const exportExcelUrl = (searchId: string) => `/api/searches/${searchId}/export/excel`
export const exportCsvUrl = (searchId: string) => `/api/searches/${searchId}/export/csv`

