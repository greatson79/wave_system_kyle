export const EMOTICONS = [
  { id: 'smile', label: '😊', name: '미소' },
  { id: 'heart', label: '❤️', name: '하트' },
  { id: 'thumbsup', label: '👍', name: '좋아요' },
  { id: 'laugh', label: '😂', name: '웃음' },
  { id: 'sad', label: '😢', name: '슬픔' },
  { id: 'angry', label: '😠', name: '화남' },
  { id: 'surprised', label: '😲', name: '놀람' },
  { id: 'thinking', label: '🤔', name: '생각' },
] as const;

export type EmoticonId = (typeof EMOTICONS)[number]['id'];

export const getEmoticonById = (id: string) => {
  return EMOTICONS.find((e) => e.id === id);
};

export const isValidEmoticonId = (id: string): id is EmoticonId => {
  return EMOTICONS.some((e) => e.id === id);
};
