import { useState, useEffect, useRef } from "react";

export function useSocket(protocol: string) {
    const socketRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        if (socketRef.current) socketRef.current.close();

        const ws = new WebSocket(`ws://localhost:8003/${protocol}`);
        socketRef.current = ws;

        ws.onopen = () => console.log("Connected:", protocol);
        ws.onerror = () => console.log("Error");
        ws.onclose = () => console.log("Closed");

        return () => ws.close();
    }, [protocol]);

    const send = (msg: string) => {
        socketRef.current?.send(msg);
    };

    return { send };
}
