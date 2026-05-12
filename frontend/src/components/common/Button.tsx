import { type ButtonHTMLAttributes } from 'react';

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  fullWidth?: boolean;
}

export const Button = ({ variant = 'primary', fullWidth, className = '', children, ...rest }: Props) => (
  <button
    className={`btn btn--${variant} ${fullWidth ? 'btn--full' : ''} ${className}`}
    {...rest}
  >
    {children}
  </button>
);
