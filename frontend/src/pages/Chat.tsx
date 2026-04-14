import { useEffect, useRef, useState } from "react";

interface Message {
    id: string;
    user: string;
    text: string;
    timestamp: number;
    isDM: boolean;
    dmRecipient?: string;
    isMyMessage: boolean;
}

export default function Chat() {
    const [message, setMessage] = useState("");
    const [messages, setMessages] = useState<Message[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [availableClients, setAvailableClients] = useState<string[]>([]);
    const [selectedRecipient, setSelectedRecipient] = useState("all");
    const [wsConnected, setWsConnected] = useState(false);

    const username = sessionStorage.getItem("username") || "Anon";
    const bottomRef = useRef<HTMLDivElement>(null);
    const wsRef = useRef<WebSocket | null>(null);
    const messageIdCounter = useRef(0);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    // Registrar cliente TCP/UDP y abrir WebSocket
    useEffect(() => {
        let cancelled = false;
        let ws: WebSocket | null = null;

        const timer = setTimeout(() => {
            if (cancelled) return;

            fetch("http://localhost:8000/client/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username }),
            })
                .then((r) => r.json())
                .then((data) => {
                    if (cancelled) return;
                    if (data.error) { setError(data.error); return; }

                    ws = new WebSocket(`ws://localhost:8000/ws/${username}`);
                    wsRef.current = ws;

                    ws.onopen = () => { setWsConnected(true); setError(""); };

                    ws.onmessage = (event) => {
                        try {
                            const msg = JSON.parse(event.data);
                            switch (msg.type) {
                                case "history":
                                    if (msg.messages && Array.isArray(msg.messages)) {
                                        setMessages(msg.messages.map((m: any) => ({
                                            id: `history-${messageIdCounter.current++}`,
                                            user: m.user, text: m.text,
                                            timestamp: m.timestamp,
                                            isDM: m.isDM || false,
                                            dmRecipient: m.dmRecipient,
                                            isMyMessage: m.user === username,
                                        })));
                                    }
                                    break;
                                case "new_message":
                                    setMessages(prev => [...prev, {
                                        id: `msg-${messageIdCounter.current++}`,
                                        user: msg.message.user, text: msg.message.text,
                                        timestamp: msg.message.timestamp,
                                        isDM: false, isMyMessage: msg.message.user === username,
                                    }]);
                                    break;
                                case "new_dm":
                                    setMessages(prev => [...prev, {
                                        id: `dm-${messageIdCounter.current++}`,
                                        user: msg.message.user, text: msg.message.text,
                                        timestamp: msg.message.timestamp,
                                        isDM: true, dmRecipient: msg.message.dmRecipient,
                                        isMyMessage: false,
                                    }]);
                                    break;
                                case "dm_sent":
                                    setMessages(prev => [...prev, {
                                        id: `dm-sent-${messageIdCounter.current++}`,
                                        user: username, text: msg.message.text,
                                        timestamp: msg.message.timestamp,
                                        isDM: true, dmRecipient: msg.message.dmRecipient,
                                        isMyMessage: true,
                                    }]);
                                    break;
                                case "clients_update":
                                    setAvailableClients(msg.clients.filter((c: string) => c !== username));
                                    break;
                            }
                        } catch {}
                    };

                    ws.onerror = () => { setError("Error de conexión con el servidor"); setWsConnected(false); };
                    ws.onclose = () => setWsConnected(false);
                })
                .catch(() => { if (!cancelled) setError("No se pudo conectar con el servidor"); });
        }, 300);

        return () => {
            cancelled = true;
            clearTimeout(timer);
            if (wsRef.current) { wsRef.current.close(); wsRef.current = null; }
        };
    }, [username]);

    async function handleSend() {
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
                // Para mensajes broadcast, agregar localmente solo si no viene por WebSocket
                if (selectedRecipient === "all") {
                    const newMsg: Message = {
                        id: `msg-local-${messageIdCounter.current++}`,
                        user: username,
                        text: message.trim(),
                        timestamp: Date.now() / 1000,
                        isDM: false,
                        isMyMessage: true
                    };
                    setMessages(prev => [...prev, newMsg]);
                }
                // Para DMs, el WebSocket enviará la confirmación
                setMessage("");
            }
        } catch (err) {
            console.error("Error enviando mensaje:", err);
            setError("Error al enviar el mensaje");
        } finally {
            setLoading(false);
        }
    }

    const sortedMessages = [...messages].sort((a, b) => a.timestamp - b.timestamp);

    return (
        <div className="mx-auto w-[40%] mt-20 flex flex-col gap-4">
            {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
                    <strong className="font-bold">Error: </strong>
                    <span className="block sm:inline">{error}</span>
                </div>
            )}

            <div className="text-right px-4 py-3 rounded bg-white/70 shadow flex justify-between items-center">
                <div className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full ${wsConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    <span className="text-sm">{wsConnected ? 'Conectado' : 'Desconectado'}</span>
                </div>
                <p className="text-sm">
                    <strong>Usuario:</strong> {username}
                </p>
            </div>

            <div className="flex flex-col gap-3 p-4 h-[60vh] overflow-y-auto bg-white/50">
                {sortedMessages.length === 0 ? (
                    <div className="text-center text-gray-500 mt-10">
                        <p>No hay mensajes aún</p>
                    </div>
                ) : (
                    sortedMessages.map((m) => (
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
                                        {m.isMyMessage ? `→ ${m.dmRecipient}` : 'Privado'}
                                    </span>
                                )}
                            </div>
                            <p>{m.text}</p>
                            {m.timestamp > 0 && (
                                <span className="text-[10px] opacity-60 block mt-1">
                                    {new Date(m.timestamp * 1000).toLocaleTimeString()}
                                </span>
                            )}
                        </div>
                    ))
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
                        disabled={loading || !wsConnected}
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
                        disabled={loading || !message.trim() || !wsConnected}
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