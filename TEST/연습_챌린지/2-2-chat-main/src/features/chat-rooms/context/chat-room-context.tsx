'use client';

import React, { createContext, useContext, useReducer, useMemo } from 'react';
import type { Message } from '@/features/messages/types';

// State 구조
type ChatRoomState = {
  replyTarget: Message | null;
  deleteMode: {
    isActive: boolean;
    selectedMessageIds: string[];
  };
  emoticonPickerOpen: boolean;
};

const initialState: ChatRoomState = {
  replyTarget: null,
  deleteMode: {
    isActive: false,
    selectedMessageIds: [],
  },
  emoticonPickerOpen: false,
};

// Actions
type ChatRoomAction =
  | { type: 'SET_REPLY_TARGET'; payload: Message | null }
  | { type: 'ENTER_DELETE_MODE'; payload: string }
  | { type: 'EXIT_DELETE_MODE' }
  | { type: 'TOGGLE_MESSAGE_SELECTION'; payload: string }
  | { type: 'TOGGLE_EMOTICON_PICKER' }
  | { type: 'RESET_AFTER_SEND' };

// Reducer
function chatRoomReducer(
  state: ChatRoomState,
  action: ChatRoomAction
): ChatRoomState {
  switch (action.type) {
    case 'SET_REPLY_TARGET':
      return {
        ...state,
        replyTarget: action.payload,
      };

    case 'ENTER_DELETE_MODE':
      return {
        ...state,
        deleteMode: {
          isActive: true,
          selectedMessageIds: [action.payload],
        },
        replyTarget: null,
        emoticonPickerOpen: false,
      };

    case 'EXIT_DELETE_MODE':
      return {
        ...state,
        deleteMode: {
          isActive: false,
          selectedMessageIds: [],
        },
      };

    case 'TOGGLE_MESSAGE_SELECTION': {
      const { selectedMessageIds } = state.deleteMode;
      const messageId = action.payload;

      return {
        ...state,
        deleteMode: {
          ...state.deleteMode,
          selectedMessageIds: selectedMessageIds.includes(messageId)
            ? selectedMessageIds.filter((id) => id !== messageId)
            : [...selectedMessageIds, messageId],
        },
      };
    }

    case 'TOGGLE_EMOTICON_PICKER':
      return {
        ...state,
        emoticonPickerOpen: !state.emoticonPickerOpen,
      };

    case 'RESET_AFTER_SEND':
      return {
        ...state,
        replyTarget: null,
        emoticonPickerOpen: false,
      };

    default:
      return state;
  }
}

// Context Value
type ChatRoomContextValue = {
  state: ChatRoomState;
  dispatch: React.Dispatch<ChatRoomAction>;
  selectedMessageCount: number;
  canDelete: boolean;
};

const ChatRoomContext = createContext<ChatRoomContextValue | undefined>(
  undefined
);

// Provider
export const ChatRoomProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [state, dispatch] = useReducer(chatRoomReducer, initialState);

  const selectedMessageCount = state.deleteMode.selectedMessageIds.length;
  const canDelete = selectedMessageCount > 0;

  const value = useMemo(
    () => ({
      state,
      dispatch,
      selectedMessageCount,
      canDelete,
    }),
    [state, selectedMessageCount, canDelete]
  );

  return (
    <ChatRoomContext.Provider value={value}>
      {children}
    </ChatRoomContext.Provider>
  );
};

// Hook
export const useChatRoomContext = () => {
  const context = useContext(ChatRoomContext);
  if (!context) {
    throw new Error(
      'useChatRoomContext must be used within ChatRoomProvider'
    );
  }
  return context;
};
