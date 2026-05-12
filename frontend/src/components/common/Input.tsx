import { type InputHTMLAttributes } from 'react';

interface Props extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = ({ label, error, className = '', ...rest }: Props) => (
  <div className="input-group">
    {label && <label className="input-label">{label}</label>}
    <input className={`input ${error ? 'input--error' : ''} ${className}`} {...rest} />
    {error && <span className="input-error">{error}</span>}
  </div>
);
