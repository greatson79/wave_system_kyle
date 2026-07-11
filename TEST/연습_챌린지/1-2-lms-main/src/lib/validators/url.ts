export const isValidUrl = (url: string): boolean => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

export const getUrlErrorMessage = (url: string): string | null => {
  if (!url) return null;
  if (!isValidUrl(url)) {
    return '올바른 URL 형식을 입력해주세요.';
  }
  return null;
};
