#pragma once
#include "platform.h"
#include <functional>
#include <string>

struct WinMessageEvent{
    std::function<void(int,int)>onRisizeEvent;//Geomatry change (x,y)
    std::function<void(int,int,int)>onMouseMoveEvent;//Mouse move windows
    //The options are x,y,bitmask
    std::function<void(int,int,int,int)>onMouseButtonEvent;//x,y,button,action
    std::function<void(int,int)>onKey;//x,y
    std::function<void()>onColseEvent;
};

class Window{
    public:
        virtual ~Window()=default;
        virtual bool create(const std::string & title ,int width,int height)=0;//The windows generat function
        virtual void destroy()=0;
        virtual void show()=0;
        virtual void hide()=0;
        virtual void pollEvent()=0;
        virtual void shouldClose()=0;
        virtual void* getNativeHandle() const = 0;
        virtual void* getNativeDisplay() const = 0;
    
        virtual int getWidth() const = 0;
        virtual int getHeight() const = 0;
    
        void setCallbacks(const WinMessageEvent& callbacks) {
            m_callbacks = callbacks;
        };
    protected:
    WinMessageEvent m_callbacks;
};
