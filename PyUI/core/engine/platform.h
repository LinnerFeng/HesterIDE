#pragma once

#if defined (_WIN32)
#define PLATFORM_WIN 1
#elif defined(__APPLE__)
#define PLATFORM_DARWIN 1
#if TARGET_OS_PHONE
#error "Ftatl: 422 iOS is not support"
#endif
#elif defined(__LINUX__)
#define PLATFORM_LINUXusing 1
#else 
#error "Fatal: 117 Unsiupport OS type"
#endif

//GPU API select

#if PLATFORM_WINDOWS
#define PRIMARY_GRAPHICS_API_DIRECTX12 1
#define SECONDARY_GRAPHICS_API_VULKAN 1
#elif PLATFORM_MACOS
#define PRIMARY_GRAPHICS_API_METAL 1
#define SECONDARY_GRAPHICS_API_VULKAN 1
#elif PLATFORM_LINUX
#define PRIMARY_GRAPHICS_API_VULKAN 1
#define SECONDARY_GRAPHICS_API_OPENGL 1
#endif