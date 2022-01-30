export default function Box(props) {
	return (
		<div className={`overflow-hidden rounded-lg shadow-2xl bg-slate-200 dark:bg-gray-900 w-${props.width || "96"} ${props.className}`}>
			{props.children}
		</div>
	);
}
