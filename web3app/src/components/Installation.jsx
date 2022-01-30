import warning from "./../warning.svg";

export default function Install() {
	return (
		<div className="w-96">
			<div className="overflow-hidden rounded-lg shadow-2xl bg-slate-200 dark:bg-gray-900">
				<div className="p-8 space-y-2 text-gray-800 dark:text-gray-300">
					<div className="md:flex md:gap-4">
						<div>
							<p className="text-lg font-bold text-black dark:text-white">You don't have MetaMask installed.</p>
							<p>
								Head over to{" "}
								<a href="https://metamask.io" className="text-blue-600 underline decoration-yellow-400 dark:text-blue-200">
									their website
								</a>{" "}
								to install the extension and come back here.
							</p>
						</div>
						<img src={warning} alt=" " className="w-0 md:w-16 hover:animate-pulse" />
					</div>

					<div className="bg-black dark:bg-white h-[1px]"></div>
					<p className="text-md">Already have MetaMask?</p>
					<p className="text-sm">
						Make sure that this website is allowed to see the <code>window.ethereum</code> object.
					</p>
				</div>
			</div>
		</div>
	);
}
