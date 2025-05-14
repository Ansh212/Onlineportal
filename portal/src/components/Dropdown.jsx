import React from "react";
import "../styles/Dropdown.css";

const Dropdown = ({ label, options, value, onChange }) => {

    return (
        <div className="dropdown-wrapper">
            <label htmlFor={`dropdown-${label}`} className="dropdown-label">
                {label}
            </label>
            <select
                id={`dropdown-${label}`}
                className="dropdown-select"
                value={value}
                onChange={(e) => onChange(e.target.value)}
            >
                <option value="" disabled>
                    Select an option
                </option>
                {options.map((option, index) => (
                    <option key={index} value={option.value}>
                        {option.label}
                    </option>
                ))}
            </select>
        </div>
    );
};

export default Dropdown;
