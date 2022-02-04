export default function Box({width, className, children}) {
	return (
		<div className={`block overflow-hidden rounded-lg shadow-2xl bg-slate-200 dark:bg-gray-900 max-w-${width || "96"} ${className}`}>{children}</div>
	);
}
