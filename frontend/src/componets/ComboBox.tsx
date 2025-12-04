import { Select, Option } from "@material-tailwind/react";

export function ComboBox() {
    return (
        <div className="w-50">
            <Select label="Protocolo">
                <Option className="text-left">TCP</Option>
                <Option className="text-left">UDP</Option>
            </Select>
        </div>
    );
}