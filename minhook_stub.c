#include "include/MinHook.h"

MH_STATUS WINAPI MH_Initialize(VOID) { return MH_OK; }
MH_STATUS WINAPI MH_Uninitialize(VOID) { return MH_OK; }
MH_STATUS WINAPI MH_CreateHook(LPVOID pTarget, LPVOID pDetour,
                               LPVOID *ppOriginal) {
  return MH_OK;
}
MH_STATUS WINAPI MH_CreateHookApi(LPCWSTR pszModule, LPCSTR pszProcName,
                                  LPVOID pDetour, LPVOID *ppOriginal) {
  return MH_OK;
}
MH_STATUS WINAPI MH_CreateHookApiEx(LPCWSTR pszModule, LPCSTR pszProcName,
                                    LPVOID pDetour, LPVOID *ppOriginal,
                                    LPVOID *ppTarget) {
  return MH_OK;
}
MH_STATUS WINAPI MH_EnableHook(LPVOID pTarget) { return MH_OK; }
MH_STATUS WINAPI MH_DisableHook(LPVOID pTarget) { return MH_OK; }
MH_STATUS WINAPI MH_QueueEnableHook(LPVOID pTarget) { return MH_OK; }
MH_STATUS WINAPI MH_QueueDisableHook(LPVOID pTarget) { return MH_OK; }
MH_STATUS WINAPI MH_ApplyQueued(VOID) { return MH_OK; }
const char *WINAPI MH_StatusToString(MH_STATUS status) { return "MH_OK"; }
