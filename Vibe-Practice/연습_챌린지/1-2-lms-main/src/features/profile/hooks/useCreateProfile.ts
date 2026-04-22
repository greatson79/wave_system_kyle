import { useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/remote/api-client'
import type { CreateProfileInput, ProfileResponse } from '../lib/dto'

export const useCreateProfile = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (input: CreateProfileInput) => {
      const response = await apiClient.post('/api/profile', input)
      return response.data as ProfileResponse
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] })
    },
  })
}
