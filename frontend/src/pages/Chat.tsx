import { useEffect, useRef, useState } from "react";
import { Textarea } from "@material-tailwind/react";
import { IconButton } from "@material-tailwind/react";

function formatMessages(history: string[]) {
    return history.map((raw, index) => {
        const [msg, ts] = raw.includes("|") ? raw.split("|") : [raw, null];
        const firstColon = msg.indexOf(":");
        if (firstColon === -1) return null;
        const user = msg.slice(0, firstColon).trim();
        const text = msg.slice(firstColon + 1).trim();
        return {
            id: index,
            user,
            text,
            timestamp: ts ? new Date(parseFloat(ts) * 1000) : null,
        };
    }).filter(Boolean);
}

export default function Chat() {
    const [message, setMessage] = useState("");
    const [messages, setMessages] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const username = sessionStorage.getItem("username") || "Anon";
    const bottomRef = useRef<HTMLDivElement>(null);
    const lastHistoryLength = useRef(0);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    async function loadHistory() {
        try {
            const res = await fetch("http://localhost:8000/client/history");
            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }
            const data = await res.json();
            if (data.history.length !== lastHistoryLength.current) {
                setMessages(formatMessages(data.history));
                lastHistoryLength.current = data.history.length;
            }
            setError("");
        } catch (err) {
            console.error("Error al cargar historial:", err);
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
        setLoading(true);
        setError("");
        try {
            const res = await fetch("http://localhost:8000/client/send", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: message.trim(),
                    username,
                }),
            });
            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }
            const data = await res.json();
            if (data.error) {
                setError(data.error);
                alert("Error: " + data.error);
            } else {
                setMessage("");
                setTimeout(loadHistory, 100);
            }
        } catch (err) {
            console.error("Error enviando mensaje:", err);
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="mx-auto w-[40%] mt-20 flex flex-col gap-4">
            {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
                    <strong className="font-bold">Error: </strong>
                    <span className="block sm:inline">{error}</span>
                </div>
            )}
            <div className="text-right px-4 py-3 rounded bg-white/70 shadow">
                <p className="text-sm">
                    <strong>Usuario:</strong> {username}
                </p>
            </div>

            <div className="flex flex-col gap-3 p-4 h-[60vh] overflow-y-auto bg-white/50">
                {messages.length === 0 ? (
                    <div className="text-center text-gray-500 mt-10">
                        <p>No hay mensajes aún</p>
                    </div>
                ) : (
                    messages.map((m) => (
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
                    ))
                )}
                <div ref={bottomRef}></div>
            </div>

            <form onSubmit={handleSend} className="flex gap-2 bg-white/70 backdrop-blur p-3 rounded-xl shadow-xl">
                <Textarea
                    value={message}
                    rows={1}
                    resize={false}
                    placeholder="Tu Mensaje"
                    disabled={loading}
                    className="min-h-full !text-black !border-none !outline-none !shadow-none focus:!shadow-none focus:!border-none"
                    containerProps={{ className: "!bg-transparent !shadow-none !border-none" }}
                    labelProps={{ className: "before:content-none after:content-none" }}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            handleSend(e as any);
                        }
                    }}
                />

                <IconButton
                    variant="text"
                    type="submit"
                    className="rounded-full"
                    disabled={loading || !message.trim()}
                >
                    {loading ? (
                        <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                    ) : (
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none"
                            viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
                            className="h-5 w-5">
                            <path strokeLinecap="round" strokeLinejoin="round"
                                d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
                        </svg>
                    )}
                </IconButton>
            </form>
        </div>
    );
}
