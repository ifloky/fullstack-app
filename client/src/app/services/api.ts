import { createApi, fetchBaseQuery, retry } from "@reduxjs/toolkit/query/react";

const baseQuery = fetchBaseQuery({
  baseUrl: "http://localhost:8000/api",
  prepareHeaders: (headers, { getState }) => {
  //   const token = 
  //   ( getState as RootState ).auth.
    }
});

const baseQueryRetry = retry(baseQuery, { maxRetries: 1});

export const api = createApi({
  reducerPath: "splitApi",
  baseQuery: baseQueryRetry,
  refetchOnMountOrArgChange: true,
  endpoints: () => ({})
})