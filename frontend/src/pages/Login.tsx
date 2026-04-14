import { Typography, Card, Input, Button } from "@material-tailwind/react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Login() {
    const [mode, setMode] = useState<"login" | "register">("login");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [username, setUsername] = useState("");
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();
        if (!email.trim() || !password.trim()) {
            alert("Correo y contraseña son obligatorios");
            return;
        }
        if (mode === "register" && username.trim().length < 3) {
            alert("El nombre de usuario debe tener al menos 3 caracteres");
            return;
        }

        setLoading(true);
        try {
            const endpoint = mode === "login" ? "/auth/login" : "/auth/register";
            const body: Record<string, string> = { email: email.trim(), password };
            if (mode === "register") body.username = username.trim();

            const res = await fetch(`http://localhost:8000${endpoint}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body),
            });
            const data = await res.json();

            if (data.error) {
                if (data.error === "El correo ya está registrado") {
                    setMode("login");
                    alert("Ese correo ya tiene cuenta. Inicia sesión.");
                } else {
                    alert("Error: " + data.error);
                }
            } else {
                sessionStorage.setItem("username", data.username);
                navigate("/");
            }
        } catch {
            alert("Error de conexión con el servidor");
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="relative grid min-h-[100vh] w-screen place-items-center p-8">
            <div className="flex flex-col-reverse items-center justify-between gap-4 self-start absolute top-8 w-full px-8 md:flex-row">
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

            <Card className="w-full max-w-sm border border-blue-gray-50 px-8 py-10 shadow-xl shadow-blue-gray-900/10">
                <Typography variant="h4" color="blue-gray" className="mb-1 text-center">
                    {mode === "login" ? "Iniciar Sesión" : "Crear Cuenta"}
                </Typography>
                <Typography color="gray" className="font-normal opacity-70 text-center mb-6 text-sm">
                    {mode === "login"
                        ? "Ingresa tus credenciales para acceder al chat"
                        : "Regístrate para acceder al chat"}
                </Typography>

                <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                    {mode === "register" && (
                        <Input
                            label="Nombre de usuario"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            maxLength={20}
                        />
                    )}
                    <Input
                        label="Correo electrónico"
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                    />
                    <Input
                        label="Contraseña"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                    <Button className="mt-2 rounded-full" type="submit" disabled={loading}>
                        {loading ? "Cargando..." : mode === "login" ? "Entrar al Chat" : "Registrarse"}
                    </Button>
                </form>

                <Typography color="gray" className="mt-6 text-center text-sm font-normal">
                    {mode === "login" ? "¿No tienes cuenta?" : "¿Ya tienes cuenta?"}{" "}
                    <span
                        className="font-semibold text-blue-gray-900 cursor-pointer hover:underline"
                        onClick={() => setMode(mode === "login" ? "register" : "login")}
                    >
                        {mode === "login" ? "Regístrate" : "Inicia sesión"}
                    </span>
                </Typography>
            </Card>
        </div>
    );
}
