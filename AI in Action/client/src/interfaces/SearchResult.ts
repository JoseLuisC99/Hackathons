interface SearchResult {
    id: string
    title: string
    authors: string
    abstract: string
    categories: string
    embedding: number[]
    search_score: number
}

export default SearchResult;