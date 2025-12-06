import { Typography, Card } from "@material-tailwind/react";
import { Select, Option } from "@material-tailwind/react";
import { Button } from "@material-tailwind/react";
import { useState, useEffect } from "react";

export default function Server() {
    const [protocol, setProtocol] = useState("");
    const [loading, setLoading] = useState(false);
    const [serverStatus, setServerStatus] = useState<any>(null);
    const [statusLoading, setStatusLoading] = useState(false);

    async function checkServerStatus() {
        setStatusLoading(true);
        try {
            const response = await fetch("http://localhost:8000/server/status");
            if (response.ok) {
                const data = await response.json();
                setServerStatus(data);
                setLoading(data.running);
            }
        } catch (error) {
            console.error("Error obteniendo estado del servidor:", error);
        } finally {
            setStatusLoading(false);
        }
    }

    useEffect(() => {
        checkServerStatus();
        const interval = setInterval(checkServerStatus, 3000);
        return () => clearInterval(interval);
    }, []);

    async function handleRun(event: React.FormEvent<HTMLFormElement>) {
        event.preventDefault();

        if (protocol.trim() === "") {
            alert("Seleccione un protocolo antes de iniciar el servidor");
            return;
        }

        setLoading(true);

        try {
            const response = await fetch("http://localhost:8000/server/run", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    "protocol": protocol
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.error) {
                alert("Error: " + data.error);
                setLoading(false);
            } else {
                alert(`Servidor ${protocol.toUpperCase()} iniciado correctamente`);
                await checkServerStatus();
            }
        } catch (error) {
            alert("Error de conexión con el servidor");
            setLoading(false);
        }
    }

    async function handleShutdown() {
        try {
            const response = await fetch("http://localhost:8000/server/shutdown", {
                method: "POST",
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.error) {
                alert("Error: " + data.error);
            } else {
                alert("Servidor detenido correctamente");
                setLoading(false);
                await checkServerStatus();
            }
        } catch (error) {
            alert("Error de conexión con el servidor");
        }
    }

    async function handleClear() {
        const confirmed = window.confirm("¿Estás seguro de que quieres borrar todo el historial de mensajes?");

        if (!confirmed) return;

        try {
            const response = await fetch("http://localhost:8000/server/clear", {
                method: "DELETE",
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.error) {
                alert("Error: " + data.error);
            } else {
                alert("Historial de mensajes borrado correctamente");
                await checkServerStatus();
            }
        } catch (error) {
            alert("Error de conexión con el servidor");
        }
    }

    return (
        <div className="relative grid min-h-[100vh] w-screen p-8">
            <div className="flex flex-col-reverse items-center justify-between gap-4 self-start md:flex-row">
                <Card className="h-max w-max flex-row items-center border border-blue-gray-50 py-4 px-5 shadow-lg shadow-blue-gray-900/5">
                    <code className="text-blue-gray-900">
                        Redes <strong>8:30 Martes/Jueves</strong>
                    </code>
                </Card>
                <Card className="h-max w-max border border-blue-gray-50 font-semibold text-blue-gray-900 shadow-lg shadow-blue-gray-900/5">
                    <div className="py-4 pl-4 pr-5">Configuración del Servidor</div>
                </Card>
            </div>

            <div className="flex-col gap-2 pt-16 text-center">
                <Typography variant="h1" color="blue-gray" className="text-8xl">
                    Welcome Admin
                </Typography>
                <Typography variant="lead" color="blue-gray" className="opacity-70 text-2xl mt-4">
                    Inicia el servidor o cambia la configuración desde aquí.
                </Typography>

                {serverStatus && (
                    <div className="mt-6 mx-auto w-fit">
                        <Card className="p-4 bg-gray-50">
                            <div className="flex items-center gap-2">
                                <div className={`w-3 h-3 rounded-full ${serverStatus.running ? 'bg-green-500' : 'bg-red-500'}`}></div>
                                <Typography className="font-semibold">
                                    Estado: {serverStatus.running ? 'Activo' : 'Detenido'}
                                </Typography>
                            </div>
                            {serverStatus.running && (
                                <>
                                    <Typography className="text-sm mt-2">
                                        Protocolo: <strong>{serverStatus.protocol?.toUpperCase()}</strong>
                                    </Typography>
                                    <Typography className="text-sm">
                                        Clientes: <strong>{serverStatus.clients?.length || 0}</strong>
                                    </Typography>
                                    <Typography className="text-sm">
                                        Mensajes: <strong>{serverStatus.history_len || 0}</strong>
                                    </Typography>
                                </>
                            )}
                        </Card>
                    </div>
                )}

                <form onSubmit={handleRun}>
                    <div className="flex justify-center text-left mt-8 gap-4">
                        <div className="w-50">
                            <Select
                                label="Protocolo"
                                value={protocol}
                                onChange={(value?: string) => setProtocol(value || "")}
                                disabled={loading}
                            >
                                <Option value="tcp">TCP</Option>
                                <Option value="udp">UDP</Option>
                            </Select>
                        </div>
                        <Button
                            type="button"
                            variant="outlined"
                            color="blue-gray"
                            className="flex items-center gap-3"
                            onClick={handleClear}
                        >
                            Limpiar Mensajes
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                fill="none"
                                viewBox="0 0 24 24"
                                strokeWidth={2}
                                stroke="currentColor"
                                className="h-4 w-5"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99"
                                />
                            </svg>
                        </Button>
                    </div>

                    <div className="flex justify-center mt-8 gap-4">
                        {!loading ? (
                            <Button
                                className="rounded-full"
                                type="submit"
                                disabled={!protocol}
                            >
                                Iniciar Servidor
                            </Button>
                        ) : (
                            <>
                                <Button
                                    className="rounded-full"
                                    color="green"
                                    disabled
                                >
                                    Servidor Activo
                                </Button>
                                <Button
                                    className="rounded-full"
                                    color="red"
                                    type="button"
                                    onClick={handleShutdown}
                                >
                                    Detener Servidor
                                </Button>
                            </>
                        )}
                    </div>
                </form>
            </div>

            <div className="grid grid-cols-1 gap-4 self-end md:grid-cols-2 lg:grid-cols-4">
                <Card
                    shadow={false}
                    className="border border-blue-gray-50 py-4 px-5 shadow-xl shadow-transparent transition-all hover:-translate-y-4 hover:border-blue-gray-100/60 hover:shadow-blue-gray-900/5"
                >
                    <Typography variant="h5" color="blue-gray" className="mb-3 flex items-center gap-3">
                        <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 50 50">
                            <g fill="none" stroke="#000" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <circle cx="25" cy="10" r="5" />
                                <circle cx="10" cy="30" r="5" />
                                <circle cx="40" cy="30" r="5" />
                                <path d="M25 15v10" />
                                <path d="M20 30H15" />
                                <path d="M30 30h5" />
                                <path d="M25 25l-10 5" />
                                <path d="M25 25l10 5" />
                            </g>
                        </svg>
                        Cambio de Protocolo
                    </Typography>
                    <Typography color="blue-gray" className="font-normal opacity-70">
                        Desde la configuración del servidor se puede seleccionar
                        el tipo de protocolo a utilizar, ya sea TCP o UDP.
                    </Typography>
                </Card>

                <Card
                    shadow={false}
                    className="border border-blue-gray-50 py-4 px-5 shadow-xl shadow-transparent transition-all hover:-translate-y-4 hover:border-blue-gray-100/60 hover:shadow-blue-gray-900/5"
                >
                    <Typography variant="h5" color="blue-gray" className="mb-3 flex items-center gap-3">
                        <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 50 50">
                            <g fill="none" stroke="#000" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M10 25a15 15 0 113 9" />
                                <path d="M10 25H4" />
                                <path d="M7 22l-3 3 3 3" />
                                <path d="M25 15v12l8 5" />
                            </g>
                        </svg>
                        Historial de Mensajes
                    </Typography>
                    <Typography color="blue-gray" className="font-normal opacity-70">
                        Con el objetivo de que al cambiar de protocolo los mensajes no se vean
                        afectados, el servidor guarda un historial de mensajes en una lista.
                    </Typography>
                </Card>

                <Card
                    shadow={false}
                    className="border border-blue-gray-50 py-4 px-5 shadow-xl shadow-transparent transition-all hover:-translate-y-4 hover:border-blue-gray-100/60 hover:shadow-blue-gray-900/5"
                >
                    <Typography variant="h5" color="blue-gray" className="mb-3 flex items-center gap-3">
                        <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 50 50">
                            <g fill="none" stroke="#000" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                                <circle cx="25" cy="14" r="6" />
                                <circle cx="14" cy="34" r="6" />
                                <circle cx="36" cy="34" r="6" />
                                <path d="M20 18l-4 10" />
                                <path d="M30 18l4 10" />
                                <path d="M19 34h12" />
                            </g>
                        </svg>
                        Funcionalidad
                    </Typography>
                    <Typography color="blue-gray" className="font-normal opacity-70">
                        Para iniciar el Chat el usuario debe ingresar su nombre, podrá acceder a la
                        sala de Chat y enviar mensajes que los otros usuarios podrán ver en tiempo real.
                    </Typography>
                </Card>

                <Card
                    shadow={false}
                    className="border border-blue-gray-50 py-4 px-5 shadow-xl shadow-transparent transition-all hover:-translate-y-4 hover:border-blue-gray-100/60 hover:shadow-blue-gray-900/5"
                >
                    <Typography variant="h5" color="blue-gray" className="mb-3 flex items-center gap-3">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 50 50" width="28" height="28">
                            <circle cx="15" cy="18" r="7" stroke="#000" strokeWidth="2" fill="none" />
                            <circle cx="35" cy="18" r="7" stroke="#000" strokeWidth="2" fill="none" />
                            <path d="M5 42c0-7 6-12 13-12s13 5 13 12H5zm14-12c7 0 13 5 13 12h13c0-7-6-12-13-12"
                                stroke="#000" strokeWidth="2" fill="none" />
                        </svg>
                        Equipo Redes
                    </Typography>
                    <Typography color="blue-gray" className="font-normal opacity-70">
                        Nuestro equipo está conformado por David Escarcega, Roberto Cornejo y Manuel Cortez, Proyecto
                        Final de la materia de Redes. (Equipo 8)
                    </Typography>
                </Card>
            </div>
        </div>
    );
}