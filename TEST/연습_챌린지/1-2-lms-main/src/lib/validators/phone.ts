export const PHONE_REGEX = /^01[0-9]-?[0-9]{3,4}-?[0-9]{4}$/;

export const isValidPhoneNumber = (phone: string): boolean => {
  return PHONE_REGEX.test(phone);
};

export const normalizePhoneNumber = (phone: string): string => {
  return phone.replace(/-/g, '');
};
