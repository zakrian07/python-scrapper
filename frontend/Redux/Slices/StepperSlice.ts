import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import type { RootState } from "../store";

interface SteperState {
  partnumbers: string[];
  SupplierType: string;
  Supplier: string;
}
const initialState: SteperState = {
  partnumbers: [],
  SupplierType: "",
  Supplier: "",
};
export const stepperSlice = createSlice({
  name: "SteperReducer",

  initialState,
  reducers: {
    SetParnumbers: (state, action: PayloadAction<string[]>) => {
      console.log(action.payload);
      state.partnumbers = action.payload;
    },
    RemoveParnumbers: (state) => {
      state.partnumbers = [];
    },
    setSupplier: (state, action: PayloadAction<string>) => {
      console.log(action.payload);
      state.Supplier = action.payload;
    },
    RemoveSupplier: (state, action: PayloadAction<string>) => {
      state.Supplier = action.payload;
    },
    setSupplierType: (state, action: PayloadAction<string>) => {
      console.log(action.payload);
      state.SupplierType = action.payload;
    },
    RemoveSupplierType: (state, action: PayloadAction<string>) => {
      state.SupplierType = action.payload;
    },
  },
});

export const SelectPartnumbers = (state: RootState) =>
  state.SteperReducer.partnumbers;
export const SelectSupplier = (state: RootState) =>
  state.SteperReducer.Supplier;
export const selectSupplierType = (state: RootState) =>
  state.SteperReducer.SupplierType;

export const {
  SetParnumbers,
  RemoveParnumbers,
  setSupplier,
  RemoveSupplier,
  setSupplierType,
  RemoveSupplierType,
} = stepperSlice.actions;

export default stepperSlice.reducer;
