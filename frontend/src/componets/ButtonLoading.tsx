import { useState } from "react";
import { Button } from "@material-tailwind/react";

export function ButtonLoading() {
    const [loading, setLoading] = useState(false);

    const handleClick = () => {
        setLoading(true);

        setTimeout(() => {
            setLoading(false);
        }, 2000);
    };

    return (
        <div className="flex items-center gap-4">
            <Button
                className="rounded-full"
                loading={loading}
                onClick={handleClick}
            >
                {loading ? "Servidor Activo" : "Iniciar Servidor"}
            </Button>
        </div>
    );
}
