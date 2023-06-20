import { configureStore } from "@reduxjs/toolkit";
import SteperReducer from "./Slices/StepperSlice";

const store = configureStore({
  reducer: {
    SteperReducer,
  },
});

// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<typeof store.getState>;
// Inferred type: {posts: PostsState, comments: CommentsState, users: UsersState}
export type AppDispatch = typeof store.dispatch;

export default store;
