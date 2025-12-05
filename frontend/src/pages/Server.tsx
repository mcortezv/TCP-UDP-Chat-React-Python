import { Typography, Card } from "@material-tailwind/react";
import { ComboBox } from "../componets/ComboBox";
import { Select, Option } from "@material-tailwind/react";
import { ButtonLoading } from "../componets/ButtonLoading";
import { RefreshButton } from "../componets/RefreshButton";
import { Textarea } from "@material-tailwind/react";
import { useState } from "react";
import { Button } from "@material-tailwind/react";

export default function Config() {
    const [protocol, setProtocol] = useState("");
    const [loading, setLoading] = useState(false);

    async function handleRun(event: React.FormEvent<HTMLFormElement>) {
        event.preventDefault();
        try {
            if (protocol.trim() != "") {
                setLoading(true);
                const response = await fetch("http://localhost:8000/server/run", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        "protocol": protocol
                    }),
                });
                const data = await response.json();
                if (data.error) {
                    alert("Error: " + data.error);
                }
            } else {
                alert("Seleccione un protocolo antes de iniciar el servidor");
            }
        } catch (error) {
            alert("Error:" + error);
        }
    }

    async function handleShutdown(event: React.FormEvent<HTMLFormElement>) {
        event.preventDefault();
        try {
            const response = await fetch("http://localhost:8000/server/shutdown", {
                method: "POST",
            });
            const data = await response.json();
            if (data.error) {
                alert("Error: " + data.error);
            } else {
                setLoading(false);
            }
        } catch (error) {
            alert("Error:" + error);
        }
    }

    async function handleClear(event: React.FormEvent<HTMLFormElement>) {
        event.preventDefault();
        try {
            const response = await fetch("http://localhost:8000/server/clear", {
                method: "DELETE",
            });
            const data = await response.json();
            if (data.error) {
                alert("Error: " + data.error);
            } else {
                alert("Error Historial de Mensajes Borrado");
            }
        } catch (error) {
            alert("Error:" + error);
        }
    }

    async function handleSwitch(event: React.FormEvent<HTMLFormElement>) {
        event.preventDefault();
        try {
            const serverStatus = await fetch("http://localhost:8000/server/status", {
                method: "GET"
            });
            const status = await serverStatus.json();
            if (status.protocol == protocol) {
                alert("El protocolo: " + protocol.toUpperCase() + " ya esta corriendo, seleciona otro.");
            } else {
                const response = await fetch("http://localhost:8000/server/switch", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        "protocol": protocol
                    }),
                });
                const data = await response.json();
                if (data.error) {
                    alert("Error: " + data.error);
                } else {
                    alert("Protocolo cambiado con exito");
                }
            }
        } catch (error) {
            alert("Error:" + error);
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
            <div className="flex-col gap-2 pt-40 pb-40 text-center">
                <Typography variant="h1" color="blue-gray" className="text-8xl">
                    Welcome Admin
                </Typography>
                <Typography variant="lead" color="blue-gray" className="opacity-70 text-2xl mt-4">
                    Inicia el servidor o cambia la configuración desde aquí.
                </Typography>
                <form onSubmit={handleRun}>
                    <div className="flex justify-center mt-8">
                        <div className="w-50">
                            <Select label="Protocolo" onChange={(value?: string) => setProtocol(value || "")}>
                                <Option value="tcp" className="text-left">TCP</Option>
                                <Option value="udp" className="text-left">UDP</Option>
                            </Select>
                        </div>
                        <div className="flex items-center gap-4">
                            <Button
                                type="button"
                                variant="outlined"
                                color="blue-gray"
                                className="flex items-center gap-3 ml-4"
                                type="button"
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
                    </div>

                    <div className="flex justify-center mt-8">
                        <div className="flex items-center gap-4">
                            <Button
                                className="rounded-full"
                                loading={loading}
                                type="submit"
                            >
                                {loading ? "Servidor Activo" : "Iniciar Servidor"}
                            </Button>
                        </div>
                        {loading && (
                            <Button
                                className="rounded-full ml-2"
                                type="button"
                                onClick={handleShutdown}
                            >
                                Detener
                            </Button>
                        )}

                    </div>
                    {loading && (
                        <Button
                            className="rounded-full mt-4"
                            type="button"
                            onClick={handleSwitch}
                        >
                            Cambiar Protocolo
                        </Button>
                    )}
                </form>

            </div>
            <div className="grid grid-cols-1 gap-4 self-end md:grid-cols-2 lg:grid-cols-4">
                <a
                    href="https://www.material-tailwind.com/docs/react/accordion?ref=template-vite-ts"
                    target="_blank"
                    rel="noreferrer"
                >
                    <Card
                        shadow={false}
                        className="border border-blue-gray-50 py-4 px-5 shadow-xl shadow-transparent transition-all hover:-translate-y-4 hover:border-blue-gray-100/60 hover:shadow-blue-gray-900/5"
                    >
                        <Typography variant="h5" color="blue-gray" className="mb-3 flex items-center gap-3">
                            <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 50 50">
                                <g fill="none" stroke="#000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
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
                            el tipo de protocolo a utilizar, ya sea TCP (Transmission Control Protocol) o UDP (User Datagram Protocol).
                        </Typography>
                    </Card>
                </a>
                <a
                    href="https://www.material-tailwind.com/blocks?ref=template-vite-ts"
                    target="_blank"
                    rel="noreferrer"
                >
                    <Card
                        shadow={false}
                        className="border border-blue-gray-50 py-4 px-5 shadow-xl shadow-transparent transition-all hover:-translate-y-4 hover:border-blue-gray-100/60 hover:shadow-blue-gray-900/5"
                    >
                        <Typography variant="h5" color="blue-gray" className="mb-3 flex items-center gap-3">
                            <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 50 50">
                                <g fill="none" stroke="#000" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
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
                </a>
                <a
                    href="https://github.com/creativetimofficial/material-tailwind?ref=template-vite-ts"
                    target="_blank"
                    rel="noreferrer"
                >
                    <Card
                        shadow={false}
                        className="border border-blue-gray-50 py-4 px-5 shadow-xl shadow-transparent transition-all hover:-translate-y-4 hover:border-blue-gray-100/60 hover:shadow-blue-gray-900/5"
                    >
                        <Typography variant="h5" color="blue-gray" className="mb-3 flex items-center gap-3">
                            <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 50 50">
                                <g fill="none" stroke="#000" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
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
                            Para iniciar el Chat el usuario debe ingresar su nombre, podra acceder a la
                            sala de Chat y enviar mensajes que los otros usuarios podran ver en tiempo real.
                        </Typography>
                    </Card>
                </a>
                <a
                    href="https://github.com/creativetimofficial/material-tailwind?ref=template-vite-ts"
                    target="_blank"
                    rel="noreferrer"
                >
                    <Card
                        shadow={false}
                        className="border border-blue-gray-50 py-4 px-5 shadow-xl shadow-transparent transition-all hover:-translate-y-4 hover:border-blue-gray-100/60 hover:shadow-blue-gray-900/5"
                    >
                        <Typography variant="h5" color="blue-gray" className="mb-3 flex items-center gap-3">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 50 50" width="28" height="28">
                                <circle cx="15" cy="18" r="7" stroke="#000" stroke-width="2" fill="none" />
                                <circle cx="35" cy="18" r="7" stroke="#000" stroke-width="2" fill="none" />
                                <path d="M5 42c0-7 6-12 13-12s13 5 13 12H5zm14-12c7 0 13 5 13 12h13c0-7-6-12-13-12"
                                    stroke="#000" stroke-width="2" fill="none" />
                            </svg>
                            Equipo Redes
                        </Typography>
                        <Typography color="blue-gray" className="font-normal opacity-70">
                            Nuestro equipo esta conformado por David Escarcega, Roberto Cornejo y Manuel Cortez, Proyecto
                            Final de la materia de Redes. (Equipo 8)
                        </Typography>
                    </Card>
                </a>
            </div>
        </div>
    );
}