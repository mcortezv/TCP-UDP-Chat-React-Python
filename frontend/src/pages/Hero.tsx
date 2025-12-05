import { Typography, Card } from "@material-tailwind/react";
import { Input } from "@material-tailwind/react";
import { Button } from "@material-tailwind/react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";


export default function Hero() {
    const [username, setUsername] = useState("");
    const navigate = useNavigate();


    async function handleRegister(event: React.FormEvent<HTMLFormElement>) {
        event.preventDefault();
        try {
            if(username.trim() != ""){
                const response = await fetch("http://localhost:8000/client/login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        username: username,
                    }),
                });

                const data = await response.json();
                if (data.error) {
                    alert("Error: " + data.error);
                } else {
                    navigate("/chat");
                }
            } else {
                alert("El nombre de usuario no puede estar vacio");
            }
        } catch (error) {
            alert("Error:" + error);
        }
    }

    return (
        <div className="relative grid min-h-[100vh] w-screen p-8">
            <div className="flex flex-col-reverse items-center justify-between gap-4 self-start md:flex-row">
                <Card className="h-max w-max flex-row items-center border border-blue-gray-50 py-4 px-5 shadow-lg shadow-blue-gray-900/5">
                    <img src="/itson.png" alt="Itson Logo" className="mr-6 h-10" />
                    <code className="text-blue-gray-900">
                        Redes <strong>8:30 Martes/Jueves</strong>
                    </code>

                </Card>
                <Card className="h-max w-max border border-blue-gray-50 font-semibold text-blue-gray-900 shadow-lg shadow-blue-gray-900/5">
                    <div className="py-4 pl-4 pr-5">Carlos Alberto Gonzalez Vega</div>
                </Card>
            </div>
            <div className="flex-col gap-2 pt-32 pb-40 text-center">
                <Typography variant="h1" color="blue-gray" className="text-8xl animate-float delay-2200">
                    Welcome to ING-CHAT
                </Typography>
                <Typography variant="lead" color="blue-gray" className="opacity-70 text-2xl mt-4">
                    Ingresa tu nombre para identificarte y podras enviar  mensajes <br />
                    visibles para los demás usuarios activos en el Chat.
                </Typography>
                <form onSubmit={handleRegister}>
                    <div className="w-80 mx-auto mt-8">
                        <Input label="Nombre" onChange={(e) => setUsername(e.target.value)} />
                    </div>
                    <div className="mx-auto mt-8 animate-pulse-slow">
                        <Button className="w-48 h-12 rounded-full" type="submit">Entrar al Chat</Button>
                    </div>
                </form>
            </div>
            <div className="hidden md:block absolute top-[14%] left-[19%] animate-float-slow delay-100">
                <img
                    src="src\assets\vite.png"
                    alt="Vite"
                    className="w-[90px] object-contain opacity-90"
                />
            </div>
            <div className="hidden md:block absolute top-[10%] right-[26%] animate-float-slow delay-300">
                <img
                    src="src\assets\python.png"
                    alt="Python"
                    className="w-[105px] object-contain opacity-90"
                />
            </div>
            <div className="hidden md:block absolute bottom-[35%] left-[4%] animate-float-slow delay-1800">
                <img
                    src="src\assets\react.png"
                    alt="React"
                    className="w-[90px] object-contain opacity-90"
                />
            </div>
            <div className="hidden md:block absolute top-[29%] left-[6%] animate-float-slow delay-2200">
                <img
                    src="src\assets\pycharm.png"
                    alt="PyCharm"
                    className="w-[120px] object-contain opacity-90"
                />
            </div>
            <div className="hidden md:block absolute bottom-[26%] left-[17%] animate-float-slow delay-900">
                <img
                    src="src\assets\potro.png"
                    alt="Potro"
                    className="w-[330px] object-contain opacity-90"
                />
            </div>
            <div className="hidden md:block absolute top-[20%] right-[5%] animate-float-slow delay-1500">
                <img
                    src="src\assets\material.png"
                    alt="Material"
                    className="w-[80px] object-contain opacity-90"
                />
            </div>
            <div className="hidden md:block absolute bottom-[30%] right-[35%] animate-float-slow delay-100">
                <img
                    src="src\assets\ts.png"
                    alt="TypeScript"
                    className="w-[70px] object-contain opacity-90"
                />
            </div>
            <div className="hidden md:block absolute bottom-[22%] right-[7%] animate-float-slow delay-2200">
                <img
                    src="src\assets\html.png"
                    alt="Html"
                    className="w-[80px] object-contain opacity-90"
                />
            </div>
            <div className="hidden md:block absolute bottom-[20%] right-[10%] animate-float">
                <img
                    src="src\assets\carlos.png"
                    alt="Carlos"
                    className="w-[280px] object-contain opacity-90"
                />
            </div>
            <div className="grid grid-cols-1 gap-4 self-end md:grid-cols-2 lg:grid-cols-4">
                <a
                    href="https://www.material-tailwind.com/docs/react/accordion?ref=template-vite-ts"
                    target="_blank"
                    rel="noreferrer"
                >
                    <Card
                        shadow={false}
                        className="animate-pulse-slow border border-blue-gray-50 py-4 px-5 shadow-xl shadow-transparent transition-all hover:-translate-y-4 hover:border-blue-gray-100/60 hover:shadow-blue-gray-900/5"
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
                        className="delay-100 animate-pulse-slow border border-blue-gray-50 py-4 px-5 shadow-xl shadow-transparent transition-all hover:-translate-y-4 hover:border-blue-gray-100/60 hover:shadow-blue-gray-900/5"
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
                        className="delay-300 animate-pulse-slow border border-blue-gray-50 py-4 px-5 shadow-xl shadow-transparent transition-all hover:-translate-y-4 hover:border-blue-gray-100/60 hover:shadow-blue-gray-900/5"
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
                        className="delay-500 animate-pulse-slow border border-blue-gray-50 py-4 px-5 shadow-xl shadow-transparent transition-all hover:-translate-y-4 hover:border-blue-gray-100/60 hover:shadow-blue-gray-900/5"
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
