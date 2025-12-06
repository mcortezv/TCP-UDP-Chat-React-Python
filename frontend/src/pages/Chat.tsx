import { useEffect, useRef, useState } from "react";
import { Textarea } from "@material-tailwind/react";
import { IconButton } from "@material-tailwind/react";


function formatMessages(history: string[]) {
    return history.map((raw, index) => {
        const [msg, ts] = raw.includes("|") ? raw.split("|") : [raw, null];
        const firstColon = msg.indexOf(":");
        const user = msg.slice(0, firstColon).trim();
        const text = msg.slice(firstColon + 1).trim();

        return {
            id: index,
            user,
            text,
            timestamp: ts ? new Date(parseFloat(ts) * 1000) : null,
        };
    });
}

export default function Chat() {
    const [message, setMessage] = useState("");
    const [messages, setMessages] = useState<any[]>([]);
    const username = sessionStorage.getItem("username") || "Anon";
    const bottomRef = useRef<HTMLDivElement>(null);
    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    async function loadHistory() {
        try {
            const res = await fetch("http://localhost:8000/client/history");
            const data = await res.json();
            setMessages(formatMessages(data.history));
        } catch {
            console.log("Error al cargar historial");
        }
    }

    useEffect(() => {
        loadHistory();
        const interval = setInterval(loadHistory, 800);
        return () => clearInterval(interval);
    }, []);

    async function handleSend(event: React.FormEvent<HTMLFormElement>) {
        event.preventDefault();

        if (!message.trim()) return;

        try {
            await fetch("http://localhost:8000/client/send", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message,
                    username,
                }),
            });

            setMessage("");
        } catch {
            alert("Error enviando mensaje");
        }
    }

    return (
        <div className="mx-auto w-[40%] mt-10 flex flex-col gap-4">
            <div className="flex flex-col gap-3 p-4 h-[60vh] overflow-y-auto rounded-xl bg-gray-100 shadow-inner">
                {messages.map((m) => (
                    <div
                        key={m.id}
                        className={`max-w-[70%] px-4 py-2 rounded-2xl shadow break-words
                            ${m.user === username
                                ? "self-end bg-blue-600 text-white"
                                : "self-start bg-white border text-gray-900"
                            }`}
                    >
                        <p className="font-semibold text-sm">{m.user}</p>
                        <p>{m.text}</p>

                        {m.timestamp && (
                            <span className="text-[10px] opacity-60 block mt-1">
                                {m.timestamp.toLocaleTimeString()}
                            </span>
                        )}
                    </div>
                ))}
                <div ref={bottomRef}></div>
            </div>
            <form onSubmit={handleSend} className="flex gap-2 mt-40">
                <Textarea
                    value={message}
                    rows={1}
                    resize={false}
                    placeholder="Tu Mensaje"
                    className="min-h-full !border-0 !shadow-none focus:!border-transparent focus:!shadow-none"
                    containerProps={{ className: "grid h-full !border-none !shadow-none" }}
                    labelProps={{ className: "before:content-none after:content-none" }}
                    onChange={(e) => setMessage(e.target.value)}
                />

                <IconButton variant="text" type="submit" className="rounded-full">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none"
                        viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
                        className="h-5 w-5">
                        <path strokeLinecap="round" strokeLinejoin="round"
                            d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
                    </svg>
                </IconButton>
            </form>
        </div>
    );
}
