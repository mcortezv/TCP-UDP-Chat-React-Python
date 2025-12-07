import { useEffect, useRef, useState } from "react";

function formatMessages(history: string[], currentUsername: string) {

    const formatted = history.map((raw, index) => {
        const [msg, ts] = raw.includes("|") ? raw.split("|") : [raw, null];
        const firstColon = msg.indexOf(":");
        if (firstColon === -1) {
            return null;
        }

        const user = msg.slice(0, firstColon).trim();
        const text = msg.slice(firstColon + 1).trim();
        const isMyMessage = user === currentUsername;

        return {
            id: `broadcast-${index}`,
            user,
            text,
            timestamp: ts ? new Date(parseFloat(ts) * 1000) : null,
            isDM: false,
            dmRecipient: null,
            shouldShow: true,
            isMyMessage
        };
    }).filter(m => m);
    return formatted;
}

export default function Chat() {
    const [message, setMessage] = useState("");
    const [messages, setMessages] = useState<any[]>([]);
    const [dmMessages, setDmMessages] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [availableClients, setAvailableClients] = useState<string[]>([]);
    const [selectedRecipient, setSelectedRecipient] = useState("all");
    const username = sessionStorage.getItem("username") || "Anon";
    const bottomRef = useRef<HTMLDivElement>(null);
    const lastHistoryLength = useRef(0);
    const dmIdCounter = useRef(0);
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
                setMessages(formatMessages(data.history, username));
                lastHistoryLength.current = data.history.length;
            }
            setError("");
        } catch (err) {
            console.error("Error al cargar historial:", err);
        }
    }

    async function loadClients() {
        try {
            const res = await fetch("http://localhost:8000/client/clients");
            if (!res.ok) return;
            const data = await res.json();
            setAvailableClients(data.clients.filter((c: string) => c !== username));
        } catch (err) {
            console.error("Error al cargar clientes:", err);
        }
    }

    async function loadDMs() {
        try {
            const res = await fetch(`http://localhost:8000/client/dms/${username}`);
            if (!res.ok) return;
            const data = await res.json();

            if (data.dms && data.dms.length > 0) {
                const newDMs = data.dms.map((dmRaw: string) => {
                    const [msg, ts] = dmRaw.includes("|") ? dmRaw.split("|") : [dmRaw, null];
                    const firstColon = msg.indexOf(":");
                    if (firstColon === -1) return null;

                    const sender = msg.slice(0, firstColon).trim();
                    const text = msg.slice(firstColon + 1).trim();

                    return {
                        id: `dm-received-${dmIdCounter.current++}`,
                        user: sender,
                        text: text,
                        timestamp: ts ? new Date(parseFloat(ts) * 1000) : new Date(),
                        isDM: true,
                        dmRecipient: username,
                        shouldShow: true,
                        isMyMessage: false
                    };
                }).filter((dm: any) => dm !== null);

                if (newDMs.length > 0) {
                    setDmMessages(prev => [...prev, ...newDMs]);
                }
            }
        } catch (err) {
            console.error("Error al cargar DMs:", err);
        }
    }

    useEffect(() => {
        loadHistory();
        loadClients();
        loadDMs();
        const interval = setInterval(() => {
            loadHistory();
            loadClients();
            loadDMs();
        }, 800);
        return () => clearInterval(interval);
    }, []);

    async function handleSend() {
        if (!message.trim()) return;
        setLoading(true);
        setError("");

        const isDM = selectedRecipient !== "all";

        try {
            const res = await fetch("http://localhost:8000/client/send", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: message.trim(),
                    username,
                    recipient: selectedRecipient
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
                // Si es DM, agregarlo localmente
                if (isDM) {
                    const newDM = {
                        id: `dm-sent-${dmIdCounter.current++}`,
                        user: username,
                        text: message.trim(),
                        timestamp: new Date(),
                        isDM: true,
                        dmRecipient: selectedRecipient,
                        shouldShow: true,
                        isMyMessage: true
                    };
                    setDmMessages(prev => [...prev, newDM]);
                }

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
                {messages.length === 0 && dmMessages.length === 0 ? (
                    <div className="text-center text-gray-500 mt-10">
                        <p>No hay mensajes aún</p>
                    </div>
                ) : (
                    [...messages, ...dmMessages]
                        .sort((a, b) => {
                            const timeA = a.timestamp ? a.timestamp.getTime() : 0;
                            const timeB = b.timestamp ? b.timestamp.getTime() : 0;
                            return timeA - timeB;
                        })
                        .map((m) => {
                            return (
                                <div
                                    key={m.id}
                                    className={`max-w-[70%] px-4 py-2 rounded-2xl shadow break-words
                                        ${m.isMyMessage
                                            ? "self-end bg-blue-600 text-white"
                                            : "self-start bg-white border text-gray-900"
                                        }
                                        ${m.isDM ? "border-2 border-gray-400" : ""}
                                    `}
                                >
                                    <div className="flex items-center gap-2">
                                        <p className="font-semibold text-sm">{m.user}</p>
                                        {m.isDM && (
                                            <span className={`text-xs px-2 py-0.5 rounded ${m.isMyMessage
                                                ? "bg-gray-300 text-gray-900"
                                                : "bg-gray-200 text-gray-800"
                                                }`}>
                                                {m.isMyMessage ? `${m.dmRecipient}` : 'Privado'}
                                            </span>
                                        )}
                                    </div>
                                    <p>{m.text}</p>

                                    {m.timestamp && (
                                        <span className="text-[10px] opacity-60 block mt-1">
                                            {m.timestamp.toLocaleTimeString()}
                                        </span>
                                    )}
                                </div>
                            );
                        })
                )}
                <div ref={bottomRef}></div>
            </div>

            <div className="flex flex-col gap-2 bg-white/70 backdrop-blur p-3 rounded-xl shadow-xl">
                <div className="flex items-center gap-2 pb-2 border-b">
                    <label className="text-sm font-medium text-gray-700">Enviar a:</label>
                    <select
                        value={selectedRecipient}
                        onChange={(e) => setSelectedRecipient(e.target.value)}
                        className="flex-1 px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        <option value="all">Todos</option>
                        {availableClients.map((client) => (
                            <option key={client} value={client}>
                                {client} (Mensaje Directo)
                            </option>
                        ))}
                    </select>
                </div>

                <div className="flex gap-2">
                    <textarea
                        value={message}
                        rows={1}
                        placeholder={selectedRecipient === "all" ? "Mensaje para todos" : `Mensaje directo para ${selectedRecipient}`}
                        disabled={loading}
                        className="flex-1 min-h-full px-3 py-2 text-black border-none outline-none resize-none focus:outline-none"
                        onChange={(e) => setMessage(e.target.value)}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault();
                                handleSend();
                            }
                        }}
                    />

                    <button
                        onClick={handleSend}
                        disabled={loading || !message.trim()}
                        className="px-4 py-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
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
                    </button>
                </div>
            </div>
        </div>
    );
}