import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/remote/api-client'
import type { ProfileResponse } from '../lib/dto'

export const useProfile = () => {
  return useQuery({
    queryKey: ['profile'],
    queryFn: async () => {
      const response = await apiClient.get('/api/profile')
      return response.data as ProfileResponse
    },
    retry: false,
  })
}
